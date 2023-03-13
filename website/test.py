import requests

access_token = 'BQAMfaYweitDg7XoMtQh8FRYC5FRuFzI6eRMIuvPXVxJIIj3zKZZGVR-TlaKTnuRAla-gbNfuuSw8fu6w-oDGHW2yEVcLJCRGzIcSsnU03WqnsMJXLaCwAh-QxJdZ1CST_i_gijT2Sax0OJGfOqZ066XE9WxP906A7hln0UvwMfwZ8Tcjbw9jlEtHYDtgXwXeVhKZtv4n9Z-wu14uiCj1le6micyDU9V1A9VTEFCVrzVfZHISc4O-TF48AhuUqiho5sJcerzol24msHvbGfDSbc'

def get_account_info(access_token):
    # access_token = 'BQACYDnasg4aKAYeNkRW9Co2qOr9FraLidlZJwxNwAVUpqOk8C1Mk1epKPKElom57HznxsB1Z1yg1wSNGenRVIewTBchqvN3bYZVhns47qpN3_Tov4re8itZ5CKbQfgeyoyYUqXMUAF_qnWnFO4UaylQ3X2o7'
    url = "https://api.spotify.com/v1/me"
    headers = {
        "Authorization": "Bearer " + access_token,
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    response = requests.get(
        url=url, headers=headers
    )
    print('--------------------------------')
    print(response)
    print('--------------------------------')
    return response.json()


info = get_account_info(access_token)

print(info)