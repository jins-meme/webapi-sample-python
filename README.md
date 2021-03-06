# webapi-sample-python

This is a sample to acquire data from JINS MEME web api (OAuth2).

## Install dependant library

pip install oauthlib 

## data_fetch.py

This sample acquires 15-second interval data and 60-second interval data according to the OAuth2 authorization code flow and saves them in CSV.

- client_id / client_secret / redirect_uri are obtained from the JINS MEME Developers app list and rewritten.
- Set the range of the date and time you want to fetch to the data start datetime (date_from) and data end datetime (date_to) in the parameters.
- Run `python data_fetch.py`.
- (You will see a message that the redirect URL is inaccessible because you have not set up a web server for the redirect URL, but this is not a problem)
- Copy and paste the URL(contains grant code) in the address bar into the Python REPL
- The data is retrieved, converted to a pandas dataframe, and saved as CSV (15s_interval_data.csv, 60s_interval_data.csv)
