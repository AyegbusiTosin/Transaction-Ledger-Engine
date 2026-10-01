#communicator to the external bank service

import httpx

async def make_bank_transfer(
    from_account: str,
    to_account: str,
    amount
):
    async with httpx.AsyncClient() as client:

        response = await client.post(
            "http://127.0.0.1:8001/bank/transfer",
            json={
                "from_account": from_account,
                "to_account": to_account,
                "amount": str(amount)
            }
        )

    #print(response.status_code)
    #print(response.text)

    return response.json()


