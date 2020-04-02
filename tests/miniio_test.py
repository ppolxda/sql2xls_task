import io
import json
from minio import PostPolicy
from minio import Minio
from minio.error import NoSuchKey
from minio.error import ResponseError
from datetime import datetime, timedelta
from datetime import timedelta

minioClient = Minio('192.168.165.85:9000',
                    access_key='minioadmin',
                    secret_key='minioadmin',
                    secure=False)

# # presigned Put object URL for an object name, expires in 3 days.
# try:
#     print(minioClient.presigned_put_object('mybucket',
#                                            'asdasdasd/myobject2',
#                                            expires=timedelta(days=3)))
# # Response error is still possible since internally presigned does get
# # bucket location.
# except ResponseError as err:
#     print(err)

# # presigned get object URL for object name, expires in 2 days.
# try:
#     print(minioClient.presigned_get_object(
#         'mybucket', 'asdasdasd/myobject2', expires=timedelta(days=2)))
# # Response error is still possible since internally presigned does get bucket location.
# except ResponseError as err:
#     print(err)


# post_policy = PostPolicy()
# # Apply upload policy restrictions:

# # set bucket name location for uploads.
# post_policy.set_bucket_name('mybucket')
# # set key prefix for all incoming uploads.
# post_policy.set_key_startswith('myobject')
# # set content length for incoming uploads.
# post_policy.set_content_length_range(10, 1024)
# # set content-type to allow only text
# post_policy.set_content_type('text/plain')

# # set expiry 10 days into future.
# expires_date = datetime.utcnow()+timedelta(seconds=10)
# post_policy.set_expires(expires_date)
# try:
#     signed_form_data = minioClient.presigned_post_policy(post_policy)
#     print(signed_form_data)
# except ResponseError as err:
#     print(err)

xdata = json.dumps({
    'asd': 'asdas',
    'as2d': 'asdas',
    'asd42': 'asdas',
})

try:
    print(minioClient.stat_object('mybucket', 'myobjectsss'))
except NoSuchKey as err:
    print(err)
except ResponseError as err:
    print(err)

buf = io.BytesIO(xdata.encode('utf8'))
data = minioClient.put_object(
    'mybucket', 'test.json', buf, len(xdata),
    content_type='application/json'
)

print(data)

data = minioClient.get_object(
    'mybucket', 'test.json'
)

print(type(data.data), data.data)


try:
    data = minioClient.stat_object('mybucket', 'test.json')
except NoSuchKey as err:
    print(err)
except ResponseError as err:
    print(err)

print(data)
