import dateutil.parser
from fastapi import FastAPI, Response, status
from pydantic import BaseModel, validator
from dateutil import parser
import pytz
from currency_rate import get_currency_rate

app = FastAPI()

currency_list = ["EUR", "USD", "GBP", "PLN"]


class PayByLink(BaseModel):
    created_at: str = None
    currency: str = None
    amount: int = None
    description: str = None
    bank: str = None

    @validator('currency')
    def currency_match(cls, v):
        if v not in currency_list:
            raise ValueError('Currency must be in currency list')
        return v


class DirectPayment(BaseModel):
    created_at: str = None
    currency: str = None
    amount: int = None
    description: str = None
    iban: str = None

    @validator('currency')
    def currency_match(cls, v):
        if v not in currency_list:
            raise ValueError('Currency must be in currency list')
        return v


class Card(BaseModel):
    created_at: str = None
    currency: str = None
    amount: int = None
    description: str = None
    cardholder_name: str = None
    cardholder_surname: str = None
    card_number: str = None

    @validator('currency')
    def currency_match(cls, v):
        if v not in currency_list:
            raise ValueError('Currency must be in currency list')
        return v


class Payment(BaseModel):
    pay_by_link: list[PayByLink] = []
    dp: list[DirectPayment] = []
    card: list[Card] = []


@app.get("/")
def root():
    return {"message": "Hello World"}


@app.post("/report", status_code=201)
def post_report(payment: Payment, response: Response):
    result_list = []
    try:
        for info in payment.pay_by_link:
            payment_info = get_payment_info(info.created_at, 'pay_by_link', info.bank, info.description,
                                            info.amount, info.currency)
            result_list.append(payment_info)
        for info in payment.dp:
            payment_info = get_payment_info(info.created_at, 'dp', info.iban, info.description, info.amount,
                                            info.currency)
            result_list.append(payment_info)
        for info in payment.card:
            masked_card_number = info.card_number[-4:].rjust(len(info.card_number), "*")
            payment_mean = f"{info.cardholder_name} {info.cardholder_surname} {masked_card_number}"
            payment_info = get_payment_info(info.created_at, 'card', payment_mean, info.description,
                                            info.amount, info.currency)
            result_list.append(payment_info)
    except dateutil.parser.ParserError:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return
    result_list.sort(key=sort_by_key)
    return result_list


def convert_to_utc(date):
    date_string = parser.parse(date)
    object_utc = date_string.astimezone(pytz.utc)
    return object_utc


def get_payment_info(date, payment_type, payment_mean, description, amount, currency):
    payment_info = {
        "date": convert_to_utc(date).isoformat(),
        "type": payment_type,
        "payment_mean": payment_mean,
        "description": description,
        "amount": amount,
        "currency": currency,
        "amount_in_pln": round(amount * get_currency_rate(currency))
    }
    return payment_info


def sort_by_key(f):
    return f["date"]

# Optional tasks


class CustomerPayment(BaseModel):
    customer_id: int
    pay_by_link: list[PayByLink] = []
    dp: list[DirectPayment] = []
    card: list[Card] = []


customer_payments = {}


@app.post("/customer-report", status_code=201)
def post_customer_report(payment: CustomerPayment, response: Response):
    result_list = []
    try:
        for info in payment.pay_by_link:
            payment_info = get_payment_info(info.created_at, 'pay_by_link', info.bank, info.description,
                                            info.amount, info.currency)
            result_list.append(payment_info)
        for info in payment.dp:
            payment_info = get_payment_info(info.created_at, 'dp', info.iban, info.description, info.amount,
                                            info.currency)
            result_list.append(payment_info)
        for info in payment.card:
            masked_card_number = info.card_number[-4:].rjust(len(info.card_number), "*")
            payment_mean = f"{info.cardholder_name} {info.cardholder_surname} {masked_card_number}"
            payment_info = get_payment_info(info.created_at, 'card', payment_mean, info.description,
                                            info.amount, info.currency)
            result_list.append(payment_info)
    except dateutil.parser.ParserError:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return
    result_list.sort(key=sort_by_key)
    customer_payments[payment.customer_id] = result_list
    return result_list


@app.get("/customer-report/{customer_id}", status_code=200)
def get_customer_report(customer_id: int, response: Response):
    for customer, report_list in customer_payments.items():
        if customer == customer_id:
            return report_list
    else:
        response.status_code = status.HTTP_400_BAD_REQUEST
