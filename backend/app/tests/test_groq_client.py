from app.integrations.groq_client import GroqClient


def _initial_messages(country_name: str) -> list[dict[str, str]]:
    return [
        {
            "role": "user",
            "content": (
                "Create a trip.\n- Days: 1\n"
                f"- Selected country: {country_name}. Keep every day in this country.\n"
                f"- Selected destination: {country_name}."
            ),
        }
    ]


def test_development_mock_keeps_kyrgyzstan_sample_content():
    response = GroqClient(use_mock=True).chat_json(_initial_messages("Kyrgyzstan"), mode="initial")

    assert response["_provider_status"]["source"] == "mock"
    assert response["itinerary"]["days"][0]["city"] == "Bishkek"


def test_development_mock_does_not_use_kyrgyzstan_for_other_country():
    response = GroqClient(use_mock=True).chat_json(_initial_messages("Japan"), mode="initial")

    assert response["_provider_status"]["source"] == "mock"
    assert response["itinerary"]["days"] == []
    assert "Japan" in response["itinerary"]["summary"]
    assert "Bishkek" not in str(response["itinerary"])
