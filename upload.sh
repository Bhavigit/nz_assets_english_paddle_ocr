#!/bin/bash

model_type="nz_assets_text"
repo_name="$model_type"
profile="prod-access"
region="ap-southeast-2"

account_id=$(aws secretsmanager get-secret-value \
  --secret-id script_keys \
  --region "$region" \
  --profile $profile | jq --raw-output '.SecretString' | jq -r .account_number)

echo "Account ID: $account_id"

# Build docker image
docker build -t $repo_name .

# Create ECR repo if not exists
aws ecr describe-repositories \
  --repository-names $repo_name \
  --region $region \
  --profile $profile 2>/dev/null || \
aws ecr create-repository \
  --repository-name $repo_name \
  --region $region \
  --profile $profile

# Tag image
docker tag $repo_name "$account_id.dkr.ecr.$region.amazonaws.com/$repo_name"

# Login to ECR
aws ecr get-login-password \
  --region $region \
  --profile $profile | docker login \
  --username AWS \
  --password-stdin "$account_id.dkr.ecr.$region.amazonaws.com"

# Push image
docker push "$account_id.dkr.ecr.$region.amazonaws.com/$repo_name"

echo "Docker image pushed successfully."