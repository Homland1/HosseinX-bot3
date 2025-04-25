#!/usr/bin/env python3
"""
این اسکریپت برای دیپلوی اتوماتیک پروژه به سرویس Render استفاده می‌شود.
"""

import os
import json
import requests
import argparse
from dotenv import load_dotenv

# بارگذاری متغیرهای محیطی از فایل .env
load_dotenv()

# تنظیمات پایه
RENDER_API_URL = "https://api.render.com/v1"

def get_render_api_key(key_number=1):
    """دریافت کلید API رندر از متغیرهای محیطی"""
    api_key = os.environ.get(f"RENDER_API_KEY_{key_number}")
    if not api_key:
        raise ValueError(f"RENDER_API_KEY_{key_number} not found in environment variables")
    return api_key

def get_headers(api_key):
    """ایجاد هدرهای مورد نیاز برای API رندر"""
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

def get_services(api_key):
    """دریافت لیست سرویس‌های موجود در حساب رندر"""
    headers = get_headers(api_key)
    response = requests.get(f"{RENDER_API_URL}/services", headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching services: {response.status_code}")
        print(response.text)
        return []

def create_service_from_yaml(api_key, repo_url, yaml_path="./render.yaml"):
    """ایجاد سرویس‌های جدید از فایل render.yaml"""
    headers = get_headers(api_key)
    
    # خواندن محتوای فایل render.yaml
    with open(yaml_path, 'r') as file:
        yaml_content = file.read()
    
    # ارسال درخواست به API رندر
    payload = {
        "repo": repo_url,
        "yaml": yaml_content,
        "autoDeploy": "yes"
    }
    
    response = requests.post(
        f"{RENDER_API_URL}/services/yaml", 
        headers=headers, 
        json=payload
    )
    
    if response.status_code in [200, 201]:
        return response.json()
    else:
        print(f"Error creating services: {response.status_code}")
        print(response.text)
        return None

def deploy_service(api_key, service_id):
    """دیپلوی مجدد یک سرویس موجود"""
    headers = get_headers(api_key)
    
    response = requests.post(
        f"{RENDER_API_URL}/services/{service_id}/deploys", 
        headers=headers
    )
    
    if response.status_code in [200, 201]:
        return response.json()
    else:
        print(f"Error deploying service: {response.status_code}")
        print(response.text)
        return None

def create_environment_variables(api_key, service_id, env_vars):
    """تنظیم متغیرهای محیطی برای یک سرویس"""
    headers = get_headers(api_key)
    
    env_list = [{"key": key, "value": value} for key, value in env_vars.items()]
    payload = {"envVars": env_list}
    
    response = requests.put(
        f"{RENDER_API_URL}/services/{service_id}/env-vars", 
        headers=headers, 
        json=payload
    )
    
    if response.status_code in [200, 201]:
        return response.json()
    else:
        print(f"Error setting environment variables: {response.status_code}")
        print(response.text)
        return None

def main():
    parser = argparse.ArgumentParser(description="Deploy HosseinX-bot3 to Render.com")
    parser.add_argument("--api-key-number", type=int, default=1, help="Which RENDER_API_KEY to use (default: 1)")
    parser.add_argument("--repo-url", type=str, default="https://github.com/Homland1/HosseinX-bot3.git", 
                        help="GitHub repository URL")
    parser.add_argument("--list-services", action="store_true", help="List existing services")
    parser.add_argument("--deploy-service", type=str, help="Service ID to deploy")
    parser.add_argument("--create-services", action="store_true", help="Create services from render.yaml")
    
    args = parser.parse_args()
    
    try:
        api_key = get_render_api_key(args.api_key_number)
        
        if args.list_services:
            services = get_services(api_key)
            print("Available services:")
            for service in services:
                print(f"ID: {service['id']}, Name: {service['name']}, Type: {service['type']}")
        
        elif args.deploy_service:
            result = deploy_service(api_key, args.deploy_service)
            if result:
                print(f"Service deployment triggered: {result['id']}")
        
        elif args.create_services:
            result = create_service_from_yaml(api_key, args.repo_url)
            if result:
                print("Services created successfully!")
                print(json.dumps(result, indent=2))
        
        else:
            parser.print_help()
    
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()