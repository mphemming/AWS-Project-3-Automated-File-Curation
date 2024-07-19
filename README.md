# AWS-Project-3-Automated-File-Curation
This repository will contain code and steps used to curate the mooring long time series products automatically.

Project progress can be tracked here: [https://github.com/users/mphemming/projects/2/views/1 ](https://github.com/users/mphemming/projects/5)

## Project Information

The below sections will contain notes and information useful to replicate the project process.

### IAM user
MFA was enabled for the root user as recommended, and an IAM user 'Michael_developer' with console access and full admin rights was created. This IAM user will be used to work on this project. The password for this IAM user is stored in Michael's Dashlane account.

### Regions
I am working within the ap-southeast-2 (Sydney) region.

### S3 Buckets

An S3 bucket to store data and code was created with the standard option within the ap-southeast-2 (Sydney) region spread across >= 3 AZs. This bucket is called 'aws-project-3'. There are two folders in this bucket called 'Code' and 'Data'.

### Lambda

#### Python Dependencies

The following Python packages are used:

* libnetcdf==0.0.1
* xarray==2024.3.0
* numpy==1.26.4
* netcdf4==1.6.5
* h5py==3.11.0
* boto3==1.34.93
* s3fs==2024.6.1
* pickleshare==0.7.5

(TO UPDATE AS I PROGRESS)

I downloaded the files after searching for the specific package here: https://pypi.org/. 
I then zipped the 'dependencies' folder and named the archive 'dependencies.zip' and uploaded it to the 'aws-project-1-data' S3 bucket.

I used the following command in AWS CloudShell to create the Lambda layer:

```
aws lambda publish-layer-version --layer-name aws-project-3-layer --description "The Lambda Python layer including dependencies required to perform automated file curation (LTSPs)" --content S3Bucket=aws-project-3/Code/,S3Key=dependencies.zip --compatible-runtimes python3.12
```

To check that the layer was created, you can use:
```
aws lambda list-layers
```

