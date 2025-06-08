Hello There !


To execute the code , we will need some additional libraries which are mentioned in the requirement.txt file also attached with the source code .

**Assumptions and consideration:**

Both Staging and Final Tiers (Not using Medallion Architecture as not a real world scenario ) databases are assumed to be created.
The Staging tables are refreshed with each run and no history is preserved as they serve no other purpose but to stage data daily.
The Final Tier Tables (only policy, claim,invoice) create a new dataset for each day based on the column "**process_day**", if a file has landed into s3 for that day . It doesn't check for any other cases

When executed , the Schedule runs at 8 AM Everyday and reads from an S3 bucket which has been used as a staging area for this project.
The code to load your local files into s3 is also added as part of source code under the folder "lib"
AWS SecretManager has been used to store the secrets like db user, password for now . All other configurations like s3 bucket name , db_url can also be moved and ideally should be kept in SM .



Cloud-Based-Architecture
--------------------------
To Develop a similar process flow in cloud 
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
7. Failure and Success Scenarios should write to SNS topics with stakeholders in the subscription list .

Other  Considerations
------------------------------
1. Always Least privilege IAM roles for Lambda .
2. Data should be always encrypted at rest and transit  
3. Lambda is charged for execution time and memory . Always run the most optimized code
4. Define metrics and SLAs in advance and set Cloud-watch Alarms when they are breached .
5. SNS Topic subscriptions for Monitoring and alerts.

