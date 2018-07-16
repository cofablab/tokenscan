import boto3


class DynamoDB(object):
    def __init__(self, table_name):
        self.resource = self._resource()
        self.client = self._client()
        self.table = self.resource.Table(table_name)
        self.table_name = table_name

    def _resource(self):
        return boto3.resource('dynamodb')

    def _client(self):
        return boto3.client('dynamodb')

    def put_item(self, item):
        return self.table.put_item(Item=item)

    def get_item(self, key, value):
        return self.table.get_item(Key={key: value})

    def get_scan_paginator(self, attributes, page_size=100):
        paginator = self.client.get_paginator('scan')
        for page in paginator.paginate(
                TableName=self.table_name,
                AttributesToGet=[attributes],
                PaginationConfig={'PageSize': page_size}):
            yield page
