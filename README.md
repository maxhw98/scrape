# scrape
Using Python with selenium webdriver to scrape a table off a webpage written that won't let you grab a table cleanly, take the table, turn it into a data frame then stick it in a google sheets doc. 

In this webpage (app.gocryohelpers.com) thrown together by High Level (a marketing support agency), the data table we want is broken up so that each individal entry is seperated by <div> tags. 
  
The code opens the page for each client, logs in and grabs each element of the table, put it together into a data frame then uploads it to the corresponding sheet in a google sheets document. 

Included is a main file, but the selenium webdriver and geckodriver (I used firefox for this) are also needed. If you're putting the data in a sheets file, you'll also need a google sheets service file, API key and of course an account that can access the API. 

When run this code goes across the data for each client and uploads it. When a new client is added all you need to do is add the client name in one list, add the client url in another list, and then add a google sheet for the data to go. This code has saved roughly 3 hours per week for everyone at ID Marketing solutions. 
