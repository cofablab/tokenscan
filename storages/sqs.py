import boto3


class SQS(object):
    def __init__(self, queue_name):
        self.client = boto3.client('sqs')
        self.queue_name = queue_name
        self.queue_url = self.get_queue_url()

    def get_queue_url(self):
        response = self.client.get_queue_url(
            QueueName=self.queue_name,
        )
        return response['QueueUrl']

    def send_message(self, body):
        response = self.client.send_message(
            QueueUrl=self.queue_url,
            MessageBody=body
        )
        return response

    def send_fifo_message(self, body, group_id='1'):
        response = self.client.send_message(
            QueueUrl=self.queue_url,
            MessageBody=body,
            MessageGroupId=group_id,
        )
        return response

    def receive_messages(self, number_of_messages=10):
        response = self.client.receive_message(
            QueueUrl=self.queue_url,
            MaxNumberOfMessages=number_of_messages
        )
        return response.get('Messages')

    def delete_message(self, receipt_handle):
        response = self.client.delete_message(
            QueueUrl=self.queue_url,
            ReceiptHandle=receipt_handle
        )
        return response
