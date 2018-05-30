import gdax

key = "SnZaQLBZWQq1RoKR"
b64secret = "Y6tchQlTfwl6imBtMEx1Irzz2vuAImJa"
passphrase = "Lilydog6!"


auth_client = gdax.AuthenticatedClient(key, b64secret, passphrase,
                                api_url="https://api-public.sandbox.gdax.com")


print(auth_client.get_accounts())
#account_id = auth_client.get_

print(auth_client.get_product_ticker(product_id='BTC-USD'))

#print(auth_client.get_account_holds())
