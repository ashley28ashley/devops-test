from etl.transformer import DataTransformer


def test_transform_event_success():
    transformer = DataTransformer()

    raw_doc = {
        "_id": "123",
        "source": "mongo",
        "payload": {
            "title": " Concert Test ",
            "description": "Super event",
            "date": "2026-06-15T19:30:00",
            "address": {
                "city": "Paris",
                "street": "10 rue de Paris",
                "zipcode": "75001"
            },
            "price": {
                "type": "Free",
                "detail": "Entrée libre"
            },
            "contact": {
                "url": "https://event.com",
                "phone": "0102030405",
                "email": "test@mail.com"
            }
        }
    }

    enriched_doc = {
        "data": {
            "city": "Paris",
            "latitude": 48.85,
            "longitude": 2.35,
            "is_free": True,
            "main_category": "Musique",
            "confidence": 0.9
        }
    }

    result = transformer.transform_event(raw_doc, enriched_doc)

    # 🔎 Vérifications principales
    assert result is not None
    assert result["raw_id"] == "123"
    assert result["title"] == "Concert Test"
    assert result["city_name"] == "Paris"

    # 📅 Vérification date
    assert result["year"] == 2026
    assert result["month"] == 6
    assert result["day"] == 15
    assert result["season"] == "Été"
    assert result["time_period"] == "Soir"

    # 📊 Vérification stats
    stats = transformer.get_stats()
    assert stats["processed"] == 1
    assert stats["errors"] == 0
