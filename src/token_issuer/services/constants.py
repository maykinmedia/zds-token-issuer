from djchoices import ChoiceItem, DjangoChoices


class VertrouwelijkheidsAanduiding(DjangoChoices):
    openbaar = ChoiceItem("openbaar", "OPENBAAR")
    beperkt_openbaar = ChoiceItem("beperkt_openbaar", "BEPERKT OPENBAAR")
    intern = ChoiceItem("intern", "INTERN")
    zaakvertrouwelijk = ChoiceItem("zaakvertrouwelijk", "ZAAKVERTROUWELIJK")
    vertrouwelijk = ChoiceItem("vertrouwelijk", "VERTROUWELIJK")
    confidentieel = ChoiceItem("confidentieel", "CONFIDENTIEEL")
    geheim = ChoiceItem("geheim", "GEHEIM")
    zeer_geheim = ChoiceItem("zeer_geheim", "ZEER GEHEIM")
