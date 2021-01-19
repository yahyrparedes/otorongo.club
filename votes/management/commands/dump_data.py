import csv

from django.core.management import BaseCommand
from django.db.models import Q

from votes.models import Elections, Person, Ingresos, CompiledPerson, BienMueble, BienInmueble, \
    CompiledOrg, SentenciaPenal, SentenciaObliga, EduUniversitaria, EduPosgrado


class Command(BaseCommand):
    help = "Dump data for candidates"

    def add_arguments(self, parser):
        parser.add_argument('-sp', '--dump_sentencia_penal', action='store_true')
        parser.add_argument('-so', '--dump_sentencia_obligaciones', action='store_true')
        parser.add_argument('-univ', '--dump_educacion_universitaria', action='store_true')
        parser.add_argument('-postgrado', '--dump_postgrado', action='store_true')
        parser.add_argument('-malos_padres', '--malos_padres', action='store_true')


    def handle(self, *args, **options):
        if options.get("dump_sentencia_penal"):
            dump_sentencia_penal()
        elif options.get("dump_sentencia_obligaciones"):
            dump_sentencia_obligaciones()
        elif options.get("dump_educacion_universitaria"):
            dump_educacion_universitaria()
        elif options.get("dump_postgrado"):
            dump_postgrado()
        elif options.get("malos_padres"):
            malos_padres()


def dump_object(model):
    with open(f'/tmp/{model.__name__.lower()}.csv', 'w') as csvfile:
        field_names = list(model.objects.first().__dict__.keys())
        field_names.extend(
            list(Person.objects.first().__dict__.keys())
        )
        writer = csv.DictWriter(csvfile, fieldnames=field_names)
        writer.writeheader()

        for item in model.objects.all():
            output = [i for i in model.objects.filter(id=item.id).values()][0]
            person = [i for i in Person.objects.filter(id=item.person.id).values()][0]
            output.update(person)
            writer.writerow(output)


def dump_postgrado():
    dump_object(EduPosgrado)


def dump_educacion_universitaria():
    with open('/tmp/edu_universitaria.csv', 'w') as csvfile:
        field_names = list(EduUniversitaria.objects.first().__dict__.keys())
        field_names.extend(
            list(Person.objects.first().__dict__.keys())
        )
        writer = csv.DictWriter(csvfile, fieldnames=field_names)
        writer.writeheader()

        for item in EduUniversitaria.objects.all():
            output = [i for i in EduUniversitaria.objects.filter(id=item.id).values()][0]
            person = [i for i in Person.objects.filter(id=item.person.id).values()][0]
            output.update(person)
            writer.writerow(output)


def dump_sentencia_obligaciones():
    with open('/tmp/sentencias_obligaciones.csv', 'w') as csvfile:
        field_names = list(SentenciaObliga.objects.first().__dict__.keys())
        field_names.extend(
            list(Person.objects.first().__dict__.keys())
        )
        writer = csv.DictWriter(csvfile, fieldnames=field_names)
        writer.writeheader()

        for item in SentenciaObliga.objects.all():
            output = [i for i in SentenciaObliga.objects.filter(id=item.id).values()][0]
            print(output)
            person = [i for i in Person.objects.filter(id=item.person.id).values()][0]
            output.update(person)
            writer.writerow(output)


def dump_sentencia_penal():
    with open('/tmp/sentencias_penales.csv', 'w') as csvfile:
        field_names = list(SentenciaPenal.objects.first().__dict__.keys())
        field_names.extend(
            list(Person.objects.first().__dict__.keys())
        )
        writer = csv.DictWriter(csvfile, fieldnames=field_names)
        writer.writeheader()

        for item in SentenciaPenal.objects.all():
            output = [i for i in SentenciaPenal.objects.filter(id=item.id).values()][0]
            print(output)
            person = [i for i in Person.objects.filter(id=item.person.id).values()][0]
            output.update(person)
            writer.writerow(output)


def malos_padres():
    election = Elections.objects.get(name='Elecciones Generales 2021')
    data = dict()

    for person in Person.objects.filter(elections=election):
        count_obliga = person.sentenciaobliga_set.all().filter(
            Q(strMateriaSentencia__icontains='familia') | Q(strMateriaSentencia__icontains='alime')
        ).count()

        if str(person) not in data:
            data[str(person)] = 0

        data[str(person)] += count_obliga

        count_penales = person.sentenciapenal_set.all().filter(
            Q(strDelitoPenal__icontains='familia') | Q(strDelitoPenal__icontains='alime')
        ).count()
        data[str(person)] += count_penales

    with open('/tmp/malos_padres.csv', 'w') as csvfile:
        field_names = ['candidato', 'numero antecedentes penales u obligaciones con familia y alimentos']
        writer = csv.DictWriter(csvfile, fieldnames=field_names)
        writer.writeheader()

        for person, count in data.items():
            if count > 0:
                out = {
                    'candidato': person,
                    'numero antecedentes penales u obligaciones con familia y alimentos': count
                }
                writer.writerow(out)
