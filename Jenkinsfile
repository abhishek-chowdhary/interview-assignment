// Dummy Pipepline for the executing the python code.
pipeline{
    agent { label 'master' }
    parameters{
        string(name: 's3_bucket', defaultValue: '', description: 'Enter the s3 bucket url to upload the file') 
    }
    stages{
        stage("Git checkout"){
            steps{
                git branch: 'master', url: 'ssh://git@bitbucket.org:company/repo.git' 
            }
        }
        stage("Generating JSON file"){
            steps{
                echo "Executing the python code to generate json data file.."
                sh "python3 main.py"
            }
        }
        stage("Uploading artifact to S3"){
            steps{
                echo "Uploading json file to s3 bucket..."
                sh "aws s3 cp account_service_status.json ${s3_bucket}"
            }
        }
    }
}