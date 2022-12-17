import requests
import os

for k, v in os.environ.items():
    print(f'{k}={v}')

print(os.environ["TEST_SECRET"])
