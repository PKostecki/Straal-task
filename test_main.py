from fastapi.testclient import TestClient
from main import app
from currency_rate import get_currency_rate

client = TestClient(app)


def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}


def test_post_report():
    response = client.post("/report", json={"pay_by_link": [
        {
            "created_at": "2021-05-13T01:01:43-08:00",
            "currency": "EUR",
            "amount": 3000,
            "description": "Gym membership",
            "bank": "mbank"
        },
    ],
        "dp": [
            {
                "created_at": "2021-05-14T08:27:09Z",
                "currency": "USD",
                "amount": 599,
                "description": "FastFood",
                "iban": "DE91100000000123456789"
            }
        ],
        "card": [
            {
                "created_at": "2021-05-13T09:00:05+02:00",
                "currency": "PLN",
                "amount": 2450,
                "description": "REF123457",
                "cardholder_name": "John",
                "cardholder_surname": "Doe",
                "card_number": "2222222222222222"
            },
            {
                "created_at": "2021-05-14T18:32:26Z",
                "currency": "GBP",
                "amount": 1000,
                "description": "REF123456",
                "cardholder_name": "John",
                "cardholder_surname": "Doe",
                "card_number": "1111111111111111"
            }
        ],
    })
    assert response.status_code == 201
    assert response.json() == [
        {
            "date": "2021-05-13T07:00:05+00:00",
            "type": "card",
            "payment_mean": "John Doe ************2222",
            "description": "REF123457",
            "currency": "PLN",
            "amount": 2450,
            "amount_in_pln": round(2450 * get_currency_rate("PLN"))
        },
        {
            "date": "2021-05-13T09:01:43+00:00",
            "type": "pay_by_link",
            "payment_mean": "mbank",
            "description": "Gym membership",
            "currency": "EUR",
            "amount": 3000,
            "amount_in_pln": round(3000 * get_currency_rate("EUR"))
        },

        {
            "date": "2021-05-14T08:27:09+00:00",
            "type": "dp",
            "payment_mean": "DE91100000000123456789",
            "description": "FastFood",
            "currency": "USD",
            "amount": 599,
            "amount_in_pln": round(599 * get_currency_rate("USD"))
        },
        {
            "date": "2021-05-14T18:32:26+00:00",
            "type": "card",
            "payment_mean": "John Doe ************1111",
            "description": "REF123456",
            "currency": "GBP",
            "amount": 1000,
            "amount_in_pln": round(1000 * get_currency_rate("GBP"))
        }
    ]


def test_bad_date():
    response = client.post("/report", json={"pay_by_link": [
        {
            "created_at": "Bad_date",
            "currency": "EUR",
            "amount": 3000,
            "description": "Gym membership",
            "bank": "mbank"
        },
    ]})
    assert response.status_code == 400


def test_customer_payment():
    response = client.post("/customer-report", json={"customer_id": 1,
                                                     "pay_by_link": [
                                                         {
                                                             "created_at": "2021-05-13T01:01:43-08:00",
                                                             "currency": "EUR",
                                                             "amount": 3000,
                                                             "description": "Gym membership",
                                                             "bank": "mbank"
                                                         },
                                                     ]})
    assert response.status_code == 201


def test_get_customer_report():
    retrieve_response = client.get("/customer-report/1")
    assert retrieve_response.status_code == 200
    assert retrieve_response.json() == [
        {
            "date": "2021-05-13T09:01:43+00:00",
            "type": "pay_by_link",
            "payment_mean": "mbank",
            "description": "Gym membership",
            "currency": "EUR",
            "amount": 3000,
            "amount_in_pln": round(3000 * get_currency_rate("EUR"))
        }]


def test_get_wrong_customer():
    retrieve_response = client.get("/customer-report/2500")
    assert retrieve_response.status_code == 400


def test_another_customer_id():
    response = client.post("/customer-report", json={"customer_id": 17,
                                                     "card": [
                                                         {
                                                             "created_at": "2021-05-13T09:00:05+02:00",
                                                             "currency": "PLN",
                                                             "amount": 2450,
                                                             "description": "REF123457",
                                                             "cardholder_name": "John",
                                                             "cardholder_surname": "Doe",
                                                             "card_number": "2222222222222222"
                                                         },
                                                         {
                                                             "created_at": "2021-05-14T18:32:26Z",
                                                             "currency": "GBP",
                                                             "amount": 1000,
                                                             "description": "REF123456",
                                                             "cardholder_name": "John",
                                                             "cardholder_surname": "Doe",
                                                             "card_number": "1111111111111111"
                                                         }
                                                     ]})
    assert response.status_code == 201
    retrieve_response = client.get("/customer-report/17")
    assert retrieve_response.status_code == 200



