# GENIE Load Testing Instructions
This folder contains files to load test a genie instance
## Instaling required libraries
To use it install the required packages by running `pip3 -r requirements.txt` from within this folder. 
## Creating test user accounts
Ensure you are logged in with `gcloud auth login`  
Configure the project you need to create test account for with `gcloud config set project $PROJECT_ID` where $PROJECT_ID is the name of the project.  
Run the command `python3 -c "from create_users import *; create_users(NUM_USERS)"` wtih  `NUM_USERS` replaced with the max 
number of users you plan to test with e.g. if no more than 100 users will be tested at once run `python3 -c "from create_users import *; create_users(100)"`
## Running the load test
Then copy the file named `example_config.py` in the same folder and name the copy `config.py`.  
Enter the address of your genie instance api backend as the BASE_URL variable.  
Then run the command `locust --host localhost` from this directory and navigate to `http://0.0.0.0:8089/`.
You should be presented with a page with a start button.  
Click start and the results should start streaming in!

## Cleanup
Once all work is complete run the command `python3 -c "from create_users import *; delete_users()"` 
to delete all created accounts