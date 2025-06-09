Hello There !


To execute the code , we will need some additional libraries which are mentioned in the requirement.txt file also attached with the source code .

**Assumptions and consideration:**

Both Staging and Final Tiers (Not using Medallion Architecture as not a real world scenario ) databases are assumed to be created.
The Staging tables are refreshed with each run and no history is preserved as they serve no other purpose but to stage data daily.
The Final Tier Fact Tables ( policy, claim,invoice) create a new dataset for each day based on the column "**process_day**", if a file has landed into s3 for that day . It doesn't check for any other cases.
Dimension tables (product, gender , status) are created to only have the latest version at any given time .

When executed , the Schedule runs at 8 AM Everyday and reads from an S3 bucket which has been used as a staging area for this project.
The code to load your local files into s3 is also added as part of source code under the folder "lib"
AWS SecretManager has been used to store the secrets like db user, password for now . All other configurations like s3 bucket name , db_url can also be moved and ideally should be kept in SM .

NOTE : All results are attched in the "result_set" folder. 
       The ERD for the DataModeling can be found under "arch_deck"

**DashBoards using PLOTLY :**
Dashbaords have been created using PLOTLY .

1. PYPLOT_DASH.PY is the driver of all static dashbaords .

	
   1. Premium Received : **premium_received_by_month_by_invoice_status** --> general  categorization of premium received by month on the invoice to check the                                                                              statistics .
                       : **premium_received_by_month** --> Finds and highloghts any anomalies in the pattern of premiums paid when the total premium received 							   is unusually high or low compared to the average
   2. NUmber of policies Issued : **policy_issued_by_gender_product** -> clearly points out the disparity in policies that are being sold to only a 										particular section of people with only one product being favoured curently .
   3. Loss Ratio : **loss_ratio_by_product_per_year** --> finds the loss ration per year per product which can be used for accurate measures on what has gone 							wrong and where is the loss coming from .
2. Interactive_Dashboard.PY :  creates an interactive dashbaord for visualization . this isn't fully functional at this moment , but it can be hosted using github pages and can be made available with a bit of cofiguration and web hosting .
    
 NOTE : All Dashbaords can be found under the folder "dashboard"


Cloud-Based-Architecture
--------------------------

**Deploying Data Pipeline to work with AWS setup **

**Using EC2 :
**

1. Set Up AWS Environment
Set up an AWS account and the necessary permissions to create and manage resources. 
Install the AWS CLI and configure it with your credentials.

2. Create an EC2 Instance
Launch an EC2 instance:

Go to the EC2 dashboard.
Click on "Launch Instance".
Choose an Amazon Machine Image (AMI) (e.g., Amazon Linux 2).
Select an instance type (e.g., t2.micro for free tier).
Configure instance details, add storage, and configure security groups (allow SSH and any other necessary ports).
Review and launch the instance.
Connect to your EC2 instance:

Use SSH to connect to the instance: ssh -i your-key.pem ec2-user@your-instance-public-dns.
Once connected to the EC2 instance, install the necessary dependencies:

E.G 
sudo yum update -y
sudo yum install python3 -y
pip3 install boto3 sqlalchemy schedule

4. Upload the Driver Script
Upload  driver.py script to the EC2 instance. You can use SCP (Secure Copy Protocol):

scp -i your-key.pem driver.py ec2-user@your-instance-public-dns:/home/ec2-user/

5. Run the Driver Script
Navigate to the directory of the  script and run it:
cd /home/ec2-user/
python3 driver.py

6. Automate Script Execution
To ensure the script runs automatically, you can use cron jobs:

Edit the crontab:
crontab -e

Add a cron job to run the script at a specific time (e.g., daily at 8:00 AM):
0 8 * * * /usr/bin/python3 /home/ec2-user/driver.py

7. Monitor and Manage
Monitor your EC2 instance and script execution using CloudWatch for logs and alarms.



**Using Lambda :
**

1. Prepare Script for Lambda
AWS Lambda has some constraints, such as the inability to run long-running processes like schedule. 
We'll need to modify your script to be event-driven. Like Remove "schedule" and add the implementaion for Lambda :
	
     def lambda_handler(event, context):
 
		---Rest of the code here ---
		
	  return {"statusCode": 200, "body": json.dumps("Job Execution Successful !")}
	
2. Create a Lambda Function
Go to the Lambda console and click "Create function".
Choose "Author from scratch".
Configure the function:
Name: your-function-name
Runtime: Python 3.x
Role: Create a new role with basic Lambda permissions.

3. Upload the Script
Package the  script and dependencies into a ZIP file. Ensure you include all necessary libraries and modules.
Upload the ZIP file to your Lambda function.

4. Set Up Environment Variables
Add environment variables for the secrets and other configurations in the Lambda function settings.

5. Configure Triggers
Set up triggers for your Lambda function. You can use CloudWatch Events or EventBidge Schedule to schedule your Lambda function to run at specific times.

For example 
Go to CloudWatch and create a new rule.
Select "Event Source":
Event Source: Schedule
Schedule Expression: cron(0 8 * * ? *) (for daily at 8:00 AM)
Add Target:
Target: Lambda function
Function: your-function-name

6. Test Your Function
Test the  Lambda function to ensure it works correctly. You can use the "Test" feature in the Lambda console to simulate an event.



**
Proposed Cloud Architecture Design ** 

I would choose to design the following : 

1. Client program to upload file to s3.
    -- I would like to receive the files on a daily basis into an AWS bucket (locally owned) where the fields would be encrypted using an AES-256-CBC algorithm.
    -- As a practice , files would be loaded to a folder which would get created for that day and this would help to segregate the files more efficiently . 
    -- For the encryption of the data , we would need to agree on a key shared between the client and I would need to know the key to be able to decrypt the file , but its not necessary as it can always stay encrypted and no one needs to know .

2. SecretManager to Manage all secrets .
    -- I would use AWS to manage all secrets like db_url,db_name,user creds ,etc . That way , I can manage the credentials better and also keeps it safe . 
    -- Both 1 and 2 has been demonstrated in the code .


3. Scheduling through Lambda 
    --  I will use AWS Lambda to execute my python code , although Lambda has 15 mins of max time , it should be enough for this workflow 
    --  the Lambda can be scheduled as required using an EventBridge on a daily schedule

   
4. RDS for staging 
    -- We will use RDS (also demonstrated) for the staging layer . Its best for OLTP transactions

5. Glue for Data transfer to Final Tier 
    -- For triggering data from staging to AWS Glue can be used .

6. Redhsift for Final Tier
    -- Redshift is best suited for Analytical data processing and can be used due to its ability to stored petabytes of data .

7. SNS for Success and Failure Notifications
    -- Failure and Success Scenarios should write to SNS topics with stakeholders' emails  in the subscription list .

Other  Considerations
------------------------------
1. Always Least privilege IAM roles for Lambda .
2. Data should be always encrypted at rest and transit  
3. Lambda is charged for execution time and memory . Always run the most optimized code
4. Define metrics and SLAs in advance and set Cloud-watch Alarms when they are breached .
5. SNS Topic subscriptions for Monitoring and alerts.

