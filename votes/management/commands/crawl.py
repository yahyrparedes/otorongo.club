from time import sleep

from django.core.management.base import BaseCommand
import requests

from votes.models import Person, Elections, SentenciaPenal, SentenciaObliga, Department, Expediente, \
    HojaVida, BienInmueble, BienMueble, EduUniversitaria, EduPosgrado, EduBasica, EduNoUniversitaria, \
    EduTecnica, InfoAdicional


class Command(BaseCommand):
    help = "Crawl candidates from JNE page."

    def add_arguments(self, parser):
        parser.add_argument('-cl', '--crawl_lists_candidates', action='store_true',
                            help='crawl lists candidates')
        parser.add_argument('-ucl', '--update_candidates_in_lists', action='store_true',
                            help='update candidates in lists')
        parser.add_argument('-ccl', '--crawl_candidates_in_lists', action='store_true',
                            help='crawl candidates in lists')
        parser.add_argument('-csp', '--crawl_sentencia_penal', action='store_true',
                            help='crawl sentencia penal')
        parser.add_argument('-cso', '--crawl_sentencia_obliga', action='store_true',
                            help='crawl sentencia obliga')
        parser.add_argument('-ucgd', '--update_candidate_general_data', action='store_true',
                            help='update_candidate_general_data')
        parser.add_argument('-ucbi', '--update_candidate_bien_inmueble', action='store_true',
                            help='update_candidate_bien_inmueble')
        parser.add_argument('-ucbm', '--update_candidate_bien_mueble', action='store_true',
                            help='update_candidate_bien_mueble')
        parser.add_argument('-ucsp', '--update_candidate_sentencia_penal', action='store_true',
                            help='update_candidate_sentencia_penal')
        parser.add_argument('-ucso', '--update_candidate_sentencia_obliga', action='store_true',
                            help='update_candidate_sentencia_obliga')
        parser.add_argument('-ceduuniv', '--crawl_edu_universitaria', action='store_true',
                            help='crawl_edu_universitaria')
        parser.add_argument('-cpostgrado', '--crawl_posgrado', action='store_true',
                            help='crawl_posgrado')
        parser.add_argument('-cedubasica', '--crawl_edu_basica', action='store_true',
                            help='crawl_edu_basica')
        parser.add_argument('-cnouniv', '--crawl_edu_no_universitaria', action='store_true',
                            help='crawl_edu_no_universitaria')
        parser.add_argument('-cedutec', '--crawl_edu_tecnica', action='store_true',
                            help='crawl_edu_tecnica')
        parser.add_argument('-cinfoad', '--crawl_info_adicional', action='store_true',
                            help='crawl_info_adicional')

    def handle(self, *args, **options):
        if options.get("crawl_lists_candidates"):
            crawl_lists_candidates()
        elif options.get('update_candidates_in_lists'):
            update_candidates_in_lists()
        elif options.get("crawl_candidates_in_lists"):
            crawl_candidates_in_lists()
        elif options.get("crawl_sentencia_penal"):
            crawl_sentencia_penal()
        elif options.get("crawl_sentencia_obliga"):
            crawl_sentencia_obliga()
        elif options.get("update_candidate_general_data"):
            update_candidate_general_data()
        elif options.get("update_candidate_bien_inmueble"):
            update_candidate_bien_inmueble()
        elif options.get("update_candidate_bien_mueble"):
            update_candidate_bien_mueble()
        elif options.get("update_candidate_sentencia_penal"):
            update_candidate_sentencia_penal()
        elif options.get("update_candidate_sentencia_obliga"):
            update_candidate_sentencia_obliga()
        elif options.get("crawl_edu_universitaria"):
            crawl_edu_universitaria()
        elif options.get("crawl_posgrado"):
            crawl_posgrado()
        elif options.get("crawl_edu_basica"):
            crawl_edu_basica()
        elif options.get("crawl_edu_no_universitaria"):
            crawl_edu_no_universitaria()
        elif options.get("crawl_edu_tecnica"):
            crawl_edu_tecnica()
        elif options.get("crawl_info_adicional"):
            crawl_info_adicional()

election = Elections.objects.get(name='Elecciones Generales 2021')

def get_candidates():
    return Person.objects.filter(elections=election)

def crawl_lists_candidates():
    print("Crawl lists of candidates")

    # get lista de expedientes
    url = ("https://plataformaelectoral.jne.gob.pe/Expediente/"
           "BusquedaReporteAvanzadoExpediente")
    payload = {'idJuradoElectoral': 0,
               'idOrganizacionPolitica': 0,
               'idProcesoElectoral': 110,
               'idTipoExpediente': 13,
               'strUbigeo': '000000'}
    res = requests.post(url, data=payload)
    data = res.json()
    unique_ids = set()

    for i in data.get("data"):
        unique_ids.add(i['idExpediente'])

    print(f'got {len(data["data"])} expedientes')
    print(f'got unique {len(unique_ids)} expedientes')

    for item in data.get("data"):
        department, _ = Department.objects.get_or_create(name=item["strDepartamento"])

        defaults = {
            "str_cod_expediente_ext": item["strCodExpedienteExt"],
            "str_cod_expediente": item["strCodExpediente"],
            "id_organizacion_politica": item["idOrganizacionPolitica"],
            "str_organizacion_politica": item["strOrganizacionPolitica"],
            "department": department,
            "str_provincia": item["strProvincia"],
            "str_distrito": item["strDistrito"],
            "str_estado_exped": item["strEstadoExped"],
            "str_tipo_eleccion": item["strTipoEleccion"],
            "id_jurado_electoral": item["idJuradoElectoral"],
            "str_jurado_electoral": item["strJuradoElectoral"],
            "id_tipo_expediente": item["idTipoExpediente"],
            "str_tipo_expediente": item["strTipoExpediente"],
            "id_materia": item["idMateria"],
            "str_materia": item["strMateria"],
        }

        id_expediente = item["idExpediente"]
        obj, created = Expediente.objects.update_or_create(
            id_expediente=id_expediente,
            defaults=defaults,
        )
        if created:
            print(f"created {obj}")


def update_candidates_in_lists():
    """Search our stored Expedientes and search for candidates that we dont have
    in our database
    """
    election = Elections.objects.get(
        name='Elecciones Generales 2021'
    )
    base_url = 'https://plataformaelectoral.jne.gob.pe/Expediente/BuscandoCodigo?strNumExpedienteFiltro='

    created_persons = []

    for exp in Expediente.objects.filter(
        str_materia__icontains='solici'
    ).order_by('id'):
        print(exp.id)
        sleep(0.05)
        url = f"{base_url}{exp.str_cod_expediente_ext}"
        payload = {'strNumExpedienteFiltro': exp.str_cod_expediente_ext}
        res = requests.post(url, data=payload)
        data = res.json().get("data")
        if data:
            for item in data.get("lCandidatosExpediente"):
                idHojaVida = item["idHojaVida"]
                hoja_vida, _ = HojaVida.objects.get_or_create(idHojaVida=idHojaVida)
                dni = item["strDocumentoIdentidad"]
                item.pop("strDocumentoIdentidad")
                item["idHojaVida"] = hoja_vida
                person, created = Person.objects.get_or_create(
                    strDocumentoIdentidad=dni,
                )
                if created:
                    person.elections.add(election)
                    Person.objects.filter(id=person.id).update(**item)
                    person.refresh_from_db()

                    person.idHojaVida = hoja_vida
                    person.dni_number = person.strDocumentoIdentidad
                    person.first_names = person.strNombres
                    person.last_names = f'{person.strApellidoPaterno} {person.strApellidoMaterno}'
                    person.save()
                    print(f'created {person}')
                    created_persons.append(person)

    print(f'created {len(created_persons)} {created_persons}')


def crawl_candidates_in_lists():
    election = Elections.objects.get(
        name='Elecciones Generales 2021'
    )
    base_url = 'https://plataformaelectoral.jne.gob.pe/Expediente/BuscandoCodigo?strNumExpedienteFiltro='

    for exp in Expediente.objects.all():
        url = f"{base_url}{exp.str_cod_expediente_ext}"
        payload = {'strNumExpedienteFiltro': exp.str_cod_expediente_ext}
        res = requests.post(url, data=payload)
        data = res.json().get("data")
        if data:
            for item in data.get("lCandidatosExpediente"):
                idHojaVida = item["idHojaVida"]
                hoja_vida, _ = HojaVida.objects.get_or_create(idHojaVida=idHojaVida)
                dni = item["strDocumentoIdentidad"]
                item.pop("strDocumentoIdentidad")
                item["idHojaVida"] = hoja_vida
                person, created = Person.objects.get_or_create(
                    strDocumentoIdentidad=dni,
                )
                if created:
                    print(f'created {person}')
                    person.elections.add(election)
                Person.objects.filter(id=person.id).update(**item)


def update_candidate_sentencia_penal():
    base_url = "https://plataformaelectoral.jne.gob.pe/HojaVida/GetAllHVSentenciaPenal?Ids="
    candidates = get_candidates()
    candidates_count = candidates.count()

    i = 1
    for candidate in candidates:
        i += 1
        if candidate.sentenciapenal_set.all().count() > 0:
            continue

        print(f"doing candidate {i}/{candidates_count}")
        id_hoja_de_vida = candidate.idHojaVida.idHojaVida
        url = f"{base_url}{id_hoja_de_vida}-0-ASC"
        res = requests.get(url)
        data = res.json()
        items = data.get("data")

        for item in items:
            if item.get("strTengoSentenciaPenal") == "2":
                continue
            obj_id = item["idHVSentenciaPenal"]
            item.pop("idHVSentenciaPenal")
            item["idHojaVida"] = candidate.idHojaVida
            obj, created = SentenciaPenal.objects.update_or_create(
                idHVSentenciaPenal=obj_id,
                defaults=item,
            )
            obj.person = candidate
            obj.idHojaVida = candidate.idHojaVida
            obj.election = election
            obj.save()

            if created:
                print(f"created {obj}")
            else:
                print(f"updated {obj}")


def crawl_edu_universitaria():
    # "https://plataformaelectoral.jne.gob.pe/HojaVida/GetAllHVEduUniversitaria?Ids=133572-0-ASC"
    base_url = "https://plataformaelectoral.jne.gob.pe/HojaVida/GetAllHVEduUniversitaria?Ids="
    candidates = get_candidates()
    candidates_count = candidates.count()

    i = 1
    for candidate in candidates:
        print(f"doing candidate {i}/{candidates_count}")
        i += 1
        id_hoja_de_vida = candidate.idHojaVida.idHojaVida
        url = f"{base_url}{id_hoja_de_vida}-0-ASC"
        res = requests.get(url)
        data = res.json()
        items = data.get("data")

        for item in items:
            if item.get("strTengoEduUniversitaria") == "2":
                continue
            obj_id = item["idHVEduUniversitaria"]
            item.pop("idHVEduUniversitaria")
            item["idHojaVida"] = candidate.idHojaVida
            obj, created = EduUniversitaria.objects.update_or_create(
                idHVEduUniversitaria=obj_id,
                defaults=item,
            )
            obj.election = election
            obj.person = candidate
            obj.save()

            if created:
                print(f"created {obj}")
            else:
                print(f"updated {obj}")

def crawl_posgrado():
    # "https://plataformaelectoral.jne.gob.pe/HojaVida/GetAllHVPosgrado?Ids=133572-0"
    base_url = "https://plataformaelectoral.jne.gob.pe/HojaVida/GetAllHVPosgrado?Ids="
    candidates = get_candidates()
    candidates_count = candidates.count()

    i = 1
    for candidate in candidates:
        print(f"doing candidate {i}/{candidates_count}")
        i += 1
        id_hoja_de_vida = candidate.idHojaVida.idHojaVida
        url = f"{base_url}{id_hoja_de_vida}-0"
        res = requests.get(url)
        data = res.json()
        items = data.get("data")

        for item in items:
            obj_id = item["idHVPosgrado"]
            item.pop("idHVPosgrado")
            item["idHojaVida"] = candidate.idHojaVida
            obj, created = EduPosgrado.objects.update_or_create(
                idHVPosgrado=obj_id,
                defaults=item,
            )
            obj.election = election
            obj.person = candidate
            obj.save()
            if created:
                print(f"created {obj}")
            else:
                print(f"updated {obj}")


def crawl_sentencia_penal():
    base_url = "https://plataformaelectoral.jne.gob.pe/HojaVida/GetAllHVSentenciaPenal?Ids="
    candidates = get_candidates()
    candidates_count = candidates.count()

    i = 1
    for candidate in candidates:
        print(f"doing candidate {i}/{candidates_count}")
        i += 1
        id_hoja_de_vida = candidate.idHojaVida.idHojaVida
        url = f"{base_url}{id_hoja_de_vida}-0-ASC"
        res = requests.get(url)
        data = res.json()
        items = data.get("data")

        for item in items:
            if item.get("strTengoSentenciaPenal") == "2":
                continue
            obj_id = item["idHVSentenciaPenal"]
            item.pop("idHVSentenciaPenal")
            item["idHojaVida"] = candidate.idHojaVida
            obj, created = SentenciaPenal.objects.update_or_create(
                idHVSentenciaPenal=obj_id,
                defaults=item,
            )
            obj.person = candidate
            obj.save()

            if created:
                print(f"created {obj}")
            else:
                print(f"updated {obj}")


def update_candidate_sentencia_obliga():
    base_url = "https://plataformaelectoral.jne.gob.pe/HojaVida/GetAllHVSentenciaObliga?Ids="
    candidates = get_candidates()
    candidates_count = candidates.count()

    i = 1
    for candidate in candidates:
        i += 1
        if candidate.sentenciaobliga_set.all().count() > 0:
            continue
        print(f"doing candidate {i}/{candidates_count}")

        id_hoja_de_vida = candidate.idHojaVida.idHojaVida
        url = f"{base_url}{id_hoja_de_vida}-0-ASC"
        res = requests.get(url)
        data = res.json()
        items = data.get("data")

        for item in items:
            if item.get("strTengoSentenciaObliga") == "2":
                continue
            obj_id = item["idHVSentenciaObliga"]
            item.pop("idHVSentenciaObliga")
            item["idHojaVida"] = candidate.idHojaVida
            obj, created = SentenciaObliga.objects.update_or_create(
                idHVSentenciaObliga=obj_id,
                defaults=item,
            )
            obj.person = candidate
            obj.idHojaVida = candidate.idHojaVida
            obj.election = election
            obj.save()

            if created:
                print(f"created {obj}")
            else:
                print(f"updated {obj}")


def crawl_sentencia_obliga():
    base_url = "https://plataformaelectoral.jne.gob.pe/HojaVida/GetAllHVSentenciaObliga?Ids="
    candidates = get_candidates()
    candidates_count = candidates.count()

    i = 1
    for candidate in candidates:
        print(f"doing candidate {i}/{candidates_count}")
        i += 1
        id_hoja_de_vida = candidate.idHojaVida.idHojaVida
        url = f"{base_url}{id_hoja_de_vida}-0-ASC"
        res = requests.get(url)
        data = res.json()
        items = data.get("data")

        for item in items:
            if item.get("strTengoSentenciaObliga") == "2":
                continue
            obj_id = item["idHVSentenciaObliga"]
            item.pop("idHVSentenciaObliga")
            item["idHojaVida"] = candidate.idHojaVida
            obj, created = SentenciaObliga.objects.update_or_create(
                idHVSentenciaObliga=obj_id,
                defaults=item,
            )
            obj.person = candidate
            obj.save()

            if created:
                print(f"created {obj}")
            else:
                print(f"updated {obj}")


def update_candidate_general_data():
    base_url = "https://plataformaelectoral.jne.gob.pe/HojaVida/GetAllHVDatosPersonales?param="
    election = Elections.objects.get(name='Elecciones Generales 2021')
    candidates = Person.objects.filter(
        strPaisNacimiento__isnull=True,
        elections=election,
    )

    for candidate in candidates:
        print(f'processing {candidate}')
        id_hoja_de_vida = candidate.idHojaVida.idHojaVida
        id_org_politica = candidate.idOrganizacionPolitica
        id_proceso = candidate.idProcesoElectoral
        url = f"{base_url}{id_hoja_de_vida}-0-{id_org_politica}-{id_proceso}"
        res = requests.get(url)
        data = res.json()
        try:
            item = data.get("data")[0]
        except:
            print(candidate, url)
            continue

        dni = item["strDocumentoIdentidad"]
        to_pop = [
            "idOrganizacionPolitica",
            "strDocumentoIdentidad",
            "strProcesoElectoral",
            "idTipoEleccion",
            "intItem",
            "idUsuario",
            "idHojaVida",
        ]
        for i in to_pop:
            item.pop(i)

        obj, created = Person.objects.update_or_create(
            strDocumentoIdentidad=dni,
            defaults=item,
        )
        if created:
            print(f"created {obj}")
        else:
            print(f"updated {obj}")


def update_candidate_bien_inmueble():
    base_url = "https://plataformaelectoral.jne.gob.pe/HojaVida/GetAllHVBienInmueble?Ids="
    candidates = get_candidates()

    for candidate in candidates:
        if candidate.bieninmueble_set.all().count() > 0:
            continue

        id_hoja_de_vida = candidate.idHojaVida.idHojaVida
        url = f"{base_url}{id_hoja_de_vida}-0-ASC"
        res = requests.get(url)
        data = res.json()
        items = data.get("data")

        for item in items:
            if item["strTengoInmueble"] == "2":
                continue

            idHVBienInmueble = item["idHVBienInmueble"]
            item.pop("idHVBienInmueble")
            item["idHojaVida"] = candidate.idHojaVida
            obj, created = BienInmueble.objects.update_or_create(
                idHVBienInmueble=idHVBienInmueble,
                defaults=item,
            )
            obj.person = candidate
            obj.election = election
            obj.idHojaVida = candidate.idHojaVida
            obj.save()

            if created:
                print(f"created {obj}")


def update_candidate_bien_mueble():
    base_url = "https://plataformaelectoral.jne.gob.pe/HojaVida/GetAllHVBienMueble?Ids="
    candidates = get_candidates()
    candidates_count = candidates.count()

    i = 1
    for candidate in candidates:
        if candidate.bienmueble_set.all().count() > 0:
            i += 1
            continue

        print(f"doing candidate {i}/{candidates_count}")
        id_hoja_de_vida = candidate.idHojaVida.idHojaVida
        url = f"{base_url}{id_hoja_de_vida}-0-ASC"
        res = requests.get(url)
        data = res.json()
        items = data.get("data")

        for item in items:
            if item["strTengoBienMueble"] == "2":
                continue

            obj_id = item["idHVBienMueble"]
            item.pop("idHVBienMueble")
            item["idHojaVida"] = candidate.idHojaVida
            obj, created = BienMueble.objects.update_or_create(
                idHVBienMueble=obj_id,
                defaults=item,
            )

            obj.person = candidate
            obj.election = election
            obj.idHojaVida = candidate.idHojaVida

            if created:
                print(f"created {obj}")
            else:
                print(f"updated {obj}")

def crawl_edu_basica():
    # "https://plataformaelectoral.jne.gob.pe/HojaVida/GetAllHVEduBasica?Ids=133572-0"
    base_url = "https://plataformaelectoral.jne.gob.pe/HojaVida/GetAllHVEduBasica?Ids="
    candidates = get_candidates()
    candidates_count = candidates.count()

    i = 1
    for candidate in candidates:
        print(f"doing candidate {i}/{candidates_count}")
        i += 1
        id_hoja_de_vida = candidate.idHojaVida.idHojaVida
        url = f"{base_url}{id_hoja_de_vida}-0"
        res = requests.get(url)
        data = res.json()
        items = data.get("data")

        for item in items:
            obj_id = item["idHVEduBasica"]
            item.pop("idHVEduBasica")
            item["idHojaVida"] = candidate.idHojaVida
            item["person"] = candidate
            item["election"] = election
            obj, created = EduBasica.objects.update_or_create(
                idHVEduBasica=obj_id,
                defaults=item,
            )

            if created:
                print(f"created {obj}")
            else:
                print(f"updated {obj}")

def crawl_edu_no_universitaria():
    # "https://plataformaelectoral.jne.gob.pe/HojaVida/GetAllHVNoUniversitaria?Ids=133572-0"
    base_url = "https://plataformaelectoral.jne.gob.pe/HojaVida/GetAllHVNoUniversitaria?Ids="
    candidates = get_candidates()
    candidates_count = candidates.count()

    i = 1
    for candidate in candidates:
        print(f"doing candidate {i}/{candidates_count}")
        i += 1
        id_hoja_de_vida = candidate.idHojaVida.idHojaVida
        url = f"{base_url}{id_hoja_de_vida}-0"
        res = requests.get(url)
        data = res.json()
        items = data.get("data")

        for item in items:
            obj_id = item["idHVNoUniversitaria"]
            item.pop("idHVNoUniversitaria")
            item["idHojaVida"] = candidate.idHojaVida
            item["person"] = candidate
            item["election"] = election
            obj, created = EduNoUniversitaria.objects.update_or_create(
                idHVNoUniversitaria=obj_id,
                defaults=item,
            )
            if created:
                print(f"created {obj}")
            else:
                print(f"updated {obj}")

def crawl_edu_tecnica():
    # "https://plataformaelectoral.jne.gob.pe/HojaVida/GetAllHVEduTecnico?Ids=133572-0"
    base_url = "https://plataformaelectoral.jne.gob.pe/HojaVida/GetAllHVEduTecnico?Ids="
    candidates = get_candidates()
    candidates_count = candidates.count()

    i = 1
    for candidate in candidates:
        print(f"doing candidate {i}/{candidates_count}")
        i += 1
        id_hoja_de_vida = candidate.idHojaVida.idHojaVida
        url = f"{base_url}{id_hoja_de_vida}-0"
        res = requests.get(url)
        data = res.json()
        items = data.get("data")

        for item in items:
            obj_id = item["idHVEduTecnico"]
            item.pop("idHVEduTecnico")
            item.pop("strComentario")
            item["idHojaVida"] = candidate.idHojaVida
            item["person"] = candidate
            item["election"] = election
            obj, created = EduTecnica.objects.update_or_create(
                idHVEduTecnico=obj_id,
                defaults=item,
            )
            if created:
                print(f"created {obj}")
            else:
                print(f"updated {obj}")

def crawl_info_adicional():
    # "https://plataformaelectoral.jne.gob.pe/HojaVida/GetAllHVInfoAdicional?Ids=133572-0"
    base_url = "https://plataformaelectoral.jne.gob.pe/HojaVida/GetAllHVInfoAdicional?Ids="
    candidates = get_candidates()
    candidates_count = candidates.count()

    i = 1
    for candidate in candidates:
        print(f"doing candidate {i}/{candidates_count}")
        i += 1
        id_hoja_de_vida = candidate.idHojaVida.idHojaVida
        url = f"{base_url}{id_hoja_de_vida}-0"
        res = requests.get(url)
        data = res.json()
        items = data.get("data")

        for item in items:
            obj_id = item["idHVInfoAdicional"]
            item.pop("idHVInfoAdicional")
            item["idHojaVida"] = candidate.idHojaVida
            item["person"] = candidate
            item["election"] = election
            obj, created = InfoAdicional.objects.update_or_create(
                idHVInfoAdicional=obj_id,
                defaults=item,
            )
            if created:
                print(f"created {obj}")
            else:
                print(f"updated {obj}")

# incomplete
def crawl_cargo_eleccion():
    # "https://plataformaelectoral.jne.gob.pe/HojaVida/GetAllHVCargoEleccion?Ids=133572-0-ASC"
    base_url = "https://plataformaelectoral.jne.gob.pe/HojaVida/GetAllHVCargoEleccion?Ids=133572-0-ASC"
    candidates = get_candidates()
    candidates_count = candidates.count()

    i = 1
    for candidate in candidates:
        print(f"doing candidate {i}/{candidates_count}")
        i += 1
        id_hoja_de_vida = candidate.idHojaVida.idHojaVida
        url = f"{base_url}{id_hoja_de_vida}-0-ASC"
        res = requests.get(url)
        data = res.json()
        items = data.get("data")
        print(data)
        break

def crawl_cargo_partidario():
    # "https://plataformaelectoral.jne.gob.pe/HojaVida/GetAllHVCargoPartidario?Ids=133572-0-ASC"
    base_url = "https://plataformaelectoral.jne.gob.pe/HojaVida/GetAllHVCargoPartidario?Ids=133572-0-ASC"
    candidates = get_candidates()
    candidates_count = candidates.count()

    i = 1
    for candidate in candidates:
        print(f"doing candidate {i}/{candidates_count}")
        i += 1
        id_hoja_de_vida = candidate.idHojaVida.idHojaVida
        url = f"{base_url}{id_hoja_de_vida}-0-ASC"
        res = requests.get(url)
        data = res.json()
        items = data.get("data")

def crawl_renuncia_op():
    # "https://plataformaelectoral.jne.gob.pe/HojaVida/GetHVRenunciaOP?Ids=133572-0-ASC"
    base_url = "https://plataformaelectoral.jne.gob.pe/HojaVida/GetHVRenunciaOP?Ids=133572-0-ASC"
    candidates = get_candidates()
    candidates_count = candidates.count()

    i = 1
    for candidate in candidates:
        print(f"doing candidate {i}/{candidates_count}")
        i += 1
        id_hoja_de_vida = candidate.idHojaVida.idHojaVida
        url = f"{base_url}{id_hoja_de_vida}-0-ASC"
        res = requests.get(url)
        data = res.json()
        items = data.get("data")

def crawl_candidate_exp_laboral():
    # TODO
    # base_url = "https://plataformaelectoral.jne.gob.pe/HojaVida/GetAllHVExpeLaboral?Ids=133572-0-ASC"
    base_url = "https://plataformaelectoral.jne.gob.pe/HojaVida/GetAllHVExpeLaboral?Ids="
    candidates = get_candidates()

    for candidate in candidates:
        id_hoja_de_vida = candidate.idHojaVida.idHojaVida
        url = f"{base_url}{id_hoja_de_vida}-0-ASC"
        res = requests.get(url)
        data = res.json()
        try:
            item = data.get("data")[0]
        except:
            print(candidate, url)
            continue

        print(item)
        break