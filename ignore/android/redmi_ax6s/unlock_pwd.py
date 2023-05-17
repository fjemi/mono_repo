 #!/usr/bin/env python3

import hashlib


# credit goes to zhoujiazhao:
# https://blog.csdn.net/zhoujiazhao/article/details/102578244

salt = {
    'r1d': 'A2E371B0-B34B-48A5-8C40-A7133F3B5D88',
    'others': 'd44fb0960aa0-a5e6-4a30-250f-6d2df50a', }


def get_salt(serial_number: str) -> str:
    ''''''
    if "/" not in serial_number:
        return salt["r1d"]

    return "-".join(reversed(salt["others"].split("-")))


def calc_password(serial_number: str) -> str:
    ''''''
    password = serial_number + get_salt(serial_number)
    hash = hashlib.md5(password.encode())
    return hash.hexdigest()[:8]


if __name__ == "__main__":
    serial_number = '36418/K1WV99868'
    password = calc_password(serial_number)
    print(password)

'''
Gym 
- morning or night
- 8 mile run
Grocery Store
- jalopenos
- bananas
- milk
- yogurt
- mushrooms
- chicken
- 
'''