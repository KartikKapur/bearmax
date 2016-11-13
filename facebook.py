import facebook
token = 'EAAQ7z3BxdYgBAHGNIM6phWb4mH0vDCfsaQaY5rxoN4ZCzZBaKmheZCsYZAkLZCB5XLmcUKkby9N5ncCPIH58swZCp5jRhTTnEQ9aaDttl4eVYUMp8h3x954vUQ6SsX5JOPeEZAhGkdl3ot5jfy8UtgZBDIXWdkOyk51Q13C3ZBoAC2QZDZD'
graph = facebook.GRAPHAPI(token)

class Userdetails:
    def __init__(self, gender, birthday,location):
        self.gender = gender
        self.birthday= birthday
        self.location = location
    def get_demographics(self):
        return self.gender, self.birthdate

gender = graph.get_object(sex = 'gender')
birthdate = graph.get_object(birth = 'birthday')
living = graph.get_object(loc = 'location')

client = Userdetails(gender, birthdate,living)
