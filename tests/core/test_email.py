import pytest

from fastapi_auth.core.email import email_service
from fastapi_auth.crud.users import UserCRUD


@pytest.mark.asyncio
async def test_send_verification_email(
    session,
    wait_for_email,
    mailpit_message,
):
    user = await UserCRUD.create(
        session,
        email="john@example.com",
        username="itz_your_john",
        hashed_password="hashed_password",
        first_name="John",
        last_name="Doe",
    )

    verification_url = f"http://localhost:3000/verify?token=test-token-{user.id}"

    await email_service.send(
        to=user.email,
        subject="Verify your email",
        template="verify_email.html",
        context={
            "user": user,
            "verification_url": verification_url,
        },
        text=("Please verify your email by visiting:\n" f"{verification_url}"),
    )

    messages = await wait_for_email()

    assert len(messages) == 1

    message = messages[0]

    assert message["Subject"] == "Verify your email"

    full_message = await mailpit_message(message["ID"])

    assert full_message["To"][0]["Address"] == user.email

    html = full_message["HTML"]
    text = full_message["Text"]

    assert verification_url in html
    assert verification_url in text

    assert user.email in html
