#include <random>
#include <math.h>
#include <iostream>
#include <fstream>
#include <vector>
#include <stdlib.h>
#include <iostream>
#include <string>
#include <sstream>
#include <cstring>
#include <ctime>
using namespace std;

#define STARTING_BALANCE_USD 10000.0
#define MIN_POINTS_TO_PRIME_EMA 1000
//#define MAX_LINES 10

// Format of coinbase CSV file is as follows
// Timestamp,Open,High,Low,Close,Volume_(BTC),Volume_(Currency),Weighted_Price
// 1417411980,300,300,300,300,0.01,3,300
// 1515369600,16174.22,16174.23,16174.22,16174.22,5.40122442,87360.593222,16174.220219

typedef struct
{
	time_t timestamp;
	double open_price;
	double high_price;
	double low_price;
	double close_price;
	double volume_btc;
	double volume_usd;
	double weighted_price;
}coinbase_row;



std::vector<coinbase_row> LoadData(const char *fname)
{
    std::vector<coinbase_row> cbv;

    // Open the input file
    ifstream in(fname);
    if ( ! in.good()) {
        std::cerr << "ERROR: Opening file `" << fname << "' failed.\n";
	return cbv;
    }

	int line_count = 0;
	coinbase_row cb;



    string line = "";

	// Skip the header row
    getline(in, line);

#ifdef MAX_LINES
    while (getline(in, line) && (line_count++ < MAX_LINES)){
#else
    while (getline(in, line) ){
#endif
        stringstream strstr(line);

        string timestamp_str = "";
        getline(strstr,timestamp_str, ',');
	cb.timestamp = (time_t) std::stol (timestamp_str,0);

        string open_price_str = "";
        getline(strstr,open_price_str, ',');
	cb.open_price = std::stod (open_price_str,0);

        string high_price_str = "";
        getline(strstr,high_price_str, ',');
	cb.high_price = std::stod (high_price_str,0);

        string low_price_str = "";
        getline(strstr,low_price_str, ',');
	cb.low_price = std::stod (low_price_str,0);

        string close_price_str = "";
        getline(strstr,close_price_str, ',');
	cb.close_price = std::stod (close_price_str,0);

        string volume_btc_str = "";
        getline(strstr,volume_btc_str, ',');
	cb.volume_btc = std::stod (volume_btc_str);

        string volume_usd_str = "";
        getline(strstr,volume_usd_str, ',');
	cb.volume_usd = std::stod (volume_usd_str,0);

        string weighted_price_str = "";
        getline(strstr,weighted_price_str, ',');
	cb.weighted_price = std::stod (weighted_price_str,0);

/*
	cout << "str = " << line.c_str() << endl;
	cout << ctime(&cb.timestamp);
	cout << cb.open_price << endl;
	cout << cb.high_price << endl;
	cout << cb.low_price << endl;
	cout << cb.close_price << endl;
	cout << cb.volume_btc << endl;
	cout << cb.volume_usd << endl;
	cout << cb.weighted_price << endl;
*/
	cbv.push_back(cb);
    }
    in.close();

	return cbv;
}



void RunExperiment(long &num_trades, long double &cum_pnl, long double &mean_pnl, long &num_pnls, long double &sd_pnl, long double &t_stat, vector<coinbase_row> &cbv, double fast_ema_weight, double slow_ema_weight, bool show_progress=false)
{
	// Declare the EMAs and define their weights based on parameters that were provided
	double prev_fast_ema = 0;
	double fast_ema = 0;
	double fast_ema_history_weight = 1.0 - fast_ema_weight;
	double prev_slow_ema = 0;
	double slow_ema = 0;
	double slow_ema_history_weight = 1.0 - slow_ema_weight;

	// Reset number of trades
	num_trades = 0;

	// Ensure we use at least a minimum number of data points to prime the EMAs
	int num_primers = 0;
	bool ema_primed = false;

	// Starting balance
	double balance_usd = STARTING_BALANCE_USD;
	double balance_btc = 0;

	// No signals yet
	bool buy_signal = false;
	bool sell_signal = false;


	std::vector<double> pnls;

	double prev_unrealized_pnl = 0;
	double unrealized_pnl = 0;
	double this_pnl = 0;

    // Iterate and print values of vector
    for(coinbase_row n : cbv) {
	prev_slow_ema = slow_ema;
	prev_fast_ema = fast_ema;
	slow_ema = slow_ema_history_weight * slow_ema + slow_ema_weight * n.weighted_price;
	fast_ema = fast_ema_history_weight * fast_ema + fast_ema_weight * n.weighted_price;
	if (!ema_primed)
	{
		num_primers++;
		ema_primed = (num_primers > MIN_POINTS_TO_PRIME_EMA);
	}

	if (ema_primed)
	{
		// If there was a buy signal, and holding USD, then move to BTC or vice versa for sell signal - always use the worst price for this time period
		if (buy_signal && !sell_signal)
		{
			balance_btc += balance_usd / n.high_price;
			balance_usd = 0;
			num_trades++;
		}
		if (sell_signal && !buy_signal)
		{
			balance_usd += balance_btc * n.low_price;
			balance_btc = 0;
		}


		// Buy signal if fast EMA crosses from blow to above slow EMA - vice versa for Sell signal
		buy_signal = (!buy_signal && (fast_ema > slow_ema) && (prev_fast_ema <= prev_slow_ema));
		sell_signal = (!sell_signal && (fast_ema < slow_ema) && (prev_fast_ema >= prev_slow_ema));


		double unrealized_balance_usd = balance_usd + balance_btc*n.weighted_price;
		prev_unrealized_pnl = unrealized_pnl;
		unrealized_pnl = (unrealized_balance_usd - STARTING_BALANCE_USD) / STARTING_BALANCE_USD;
		this_pnl = unrealized_pnl - prev_unrealized_pnl;
		pnls.push_back(this_pnl);

		cum_pnl = unrealized_pnl;

	if (show_progress)
	{
	        std::cout << n.weighted_price << "\t" << slow_ema << "\t" << fast_ema << "\t" << (buy_signal?"B":" ") << (sell_signal?"S":" ") << "\t" << unrealized_balance_usd << "\t" << 100.0*unrealized_pnl << "%" << endl;
	}
	}
    }

	// Calculate the t-stat from the timeseries of PNLS
	long double sum_pnl = 0;

    for(double p : pnls) {
		sum_pnl += p;
	}

	mean_pnl = sum_pnl / (long double) pnls.size();
	num_pnls = pnls.size();

	long double sum_sqr_delta = 0;
    for(double p : pnls) {
		long double delta = p - mean_pnl;
		sum_sqr_delta += delta * delta;
	}

	sd_pnl = sqrt(sum_sqr_delta / (long double) (num_pnls - 1));
	t_stat = sqrt(pnls.size()) * mean_pnl / sd_pnl;

	//cout << "USD: $" << balance_usd << endl;
	//cout << "BTC: " << balance_btc << endl;
	//cout << "Number of Trades: " << num_trades << endl;

}

void ShowResults(long num_trades, long double cum_pnl, long double mean_pnl, long num_pnls, long double sd_pnl, long double t_stat, double fast_ema_weight, double slow_ema_weight)
{
	cout << "---------------------------------------------------------" << endl;
	cout << "Slow EMA weight = " << slow_ema_weight << endl;
	cout << "Fast EMA weight = " << fast_ema_weight << endl;
	cout << "Cumulative PNL  = " << 100.0*cum_pnl << "%" << endl;
	cout << "Num trades      = " << num_trades << endl;
	cout << "Num PNLs        = " << num_pnls << endl;
	cout << "Mean PNL        = " << 100.0*mean_pnl << "%" << endl;
	cout << "SD PNL          = " << sd_pnl << endl;
	cout << "T-stat          = " << t_stat << endl;
	cout << "---------------------------------------------------------" << endl;
}

int main( int argc, char*argv[]) {
    if ( argc != 2) {
	std::cerr << "Usage: " << argv[0] <<" <in-file>\n";
	return EXIT_FAILURE;
    }

    std::vector<coinbase_row> cbv = LoadData(argv[1]);

	long double cum_pnl = 0;
	long double mean_pnl = 0;
	long double sd_pnl = 0;
	long double t_stat = 0;
	long num_pnls = 0;
	long num_trades = 0;


	double slowest_ema_weight = 1.0 / (60.0*24.0*7.0); // Roughly 1 week at a data point per minute
	double fastest_ema_weight = 1.0; // Ignore all history and just use the latest data point

	// Seed with a reasonable set of weights
//	double fast_ema_weight = 0.01;
//	double slow_ema_weight = 0.0001;
//	double fast_ema_weight = 0.008;
//	double slow_ema_weight = 0.003;
	double fast_ema_weight = 0.00703268;
	double slow_ema_weight = 0.00443511;

	cout << "Running experiment" << endl;
	RunExperiment(num_trades, cum_pnl, mean_pnl, num_pnls, sd_pnl, t_stat, cbv, fast_ema_weight, slow_ema_weight);
	cout << "Experiment complete" << endl;
	ShowResults(num_trades, cum_pnl, mean_pnl, num_pnls, sd_pnl, t_stat, fast_ema_weight, slow_ema_weight);

	double best_fast_ema_weight = fast_ema_weight;
	double best_slow_ema_weight = slow_ema_weight;
	long double best_t_stat = t_stat;

	std::default_random_engine re;

	// Now keep trying random parameters, and if there's an improvement, then output the results
	while(true)
	{
		double lower_bound = slowest_ema_weight;
		double upper_bound = fastest_ema_weight;
		std::uniform_real_distribution<double> unif(lower_bound,upper_bound);
		fast_ema_weight = unif(re);

		upper_bound = fast_ema_weight;
		std::uniform_real_distribution<double> unif2(lower_bound,upper_bound);
		slow_ema_weight = unif2(re);

		RunExperiment(num_trades, cum_pnl, mean_pnl, num_pnls, sd_pnl, t_stat, cbv, fast_ema_weight, slow_ema_weight);

		if (t_stat > best_t_stat)
		{
			best_t_stat = t_stat;
			ShowResults(num_trades, cum_pnl, mean_pnl, num_pnls, sd_pnl, t_stat, fast_ema_weight, slow_ema_weight);
		}
	}

    return EXIT_SUCCESS;
}
