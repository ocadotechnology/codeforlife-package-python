# Generated by Django 3.2.20 on 2023-12-15 16:05

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('last_saved_at', models.DateTimeField(auto_now=True, help_text='Record the last time the model was saved. This is used by our data warehouse to know what data was modified since the last scheduled data transfer from the database to the data warehouse.', verbose_name='last saved at')),
                ('delete_after', models.DateTimeField(blank=True, help_text="When this data is scheduled for deletion. Set to null if not scheduled for deletion. This is used by our data warehouse to transfer data that's been scheduled for deletion before it's actually deleted. Data will actually be deleted in a CRON job after this point in time.", null=True, verbose_name='delete after')),
                ('first_name', models.CharField(max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, null=True, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, null=True, unique=True, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=False, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, editable=False, verbose_name='date joined')),
                ('otp_secret', models.CharField(editable=False, help_text='Secret used to generate a OTP.', max_length=40, null=True, verbose_name='OTP secret')),
                ('last_otp_for_time', models.DateTimeField(editable=False, help_text='Used to prevent replay attacks, where the same OTP is used for different times.', null=True, verbose_name='last OTP for-time')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
            },
        ),
        migrations.CreateModel(
            name='AuthFactor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_saved_at', models.DateTimeField(auto_now=True, help_text='Record the last time the model was saved. This is used by our data warehouse to know what data was modified since the last scheduled data transfer from the database to the data warehouse.', verbose_name='last saved at')),
                ('delete_after', models.DateTimeField(blank=True, help_text="When this data is scheduled for deletion. Set to null if not scheduled for deletion. This is used by our data warehouse to transfer data that's been scheduled for deletion before it's actually deleted. Data will actually be deleted in a CRON job after this point in time.", null=True, verbose_name='delete after')),
                ('type', models.TextField(choices=[('otp', 'one-time password')], help_text='The type of authentication factor.', verbose_name='auth factor type')),
            ],
            options={
                'verbose_name': 'auth factor',
                'verbose_name_plural': 'auth factors',
            },
        ),
        migrations.CreateModel(
            name='Class',
            fields=[
                ('last_saved_at', models.DateTimeField(auto_now=True, help_text='Record the last time the model was saved. This is used by our data warehouse to know what data was modified since the last scheduled data transfer from the database to the data warehouse.', verbose_name='last saved at')),
                ('delete_after', models.DateTimeField(blank=True, help_text="When this data is scheduled for deletion. Set to null if not scheduled for deletion. This is used by our data warehouse to transfer data that's been scheduled for deletion before it's actually deleted. Data will actually be deleted in a CRON job after this point in time.", null=True, verbose_name='delete after')),
                ('id', models.CharField(editable=False, help_text='Uniquely identifies a class.', max_length=5, primary_key=True, serialize=False, validators=[django.core.validators.MinLengthValidator(5), django.core.validators.RegexValidator(code='id_not_upper_alphanumeric', message='ID must be alphanumeric with upper case characters.', regex='^[0-9A-Z]*$')], verbose_name='identifier')),
                ('name', models.CharField(max_length=200, verbose_name='name')),
                ('read_classmates_data', models.BooleanField(default=False, help_text="Designates whether students in this class can see their fellow classmates' data.", verbose_name='read classmates data')),
                ('receive_requests_until', models.DateTimeField(help_text="A point in the future until which the class can receive requests from students to join. Set to null if it's not accepting requests.", null=True, verbose_name='accept student join requests until')),
            ],
            options={
                'verbose_name': 'class',
                'verbose_name_plural': 'classes',
            },
        ),
        migrations.CreateModel(
            name='OtpBypassToken',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token', models.CharField(max_length=8, validators=[django.core.validators.MinLengthValidator(8)])),
            ],
            options={
                'verbose_name': 'OTP bypass token',
                'verbose_name_plural': 'OTP bypass tokens',
            },
        ),
        migrations.CreateModel(
            name='School',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_saved_at', models.DateTimeField(auto_now=True, help_text='Record the last time the model was saved. This is used by our data warehouse to know what data was modified since the last scheduled data transfer from the database to the data warehouse.', verbose_name='last saved at')),
                ('delete_after', models.DateTimeField(blank=True, help_text="When this data is scheduled for deletion. Set to null if not scheduled for deletion. This is used by our data warehouse to transfer data that's been scheduled for deletion before it's actually deleted. Data will actually be deleted in a CRON job after this point in time.", null=True, verbose_name='delete after')),
                ('name', models.CharField(help_text="The school's name.", max_length=200, unique=True, verbose_name='name')),
                ('country', models.TextField(blank=True, choices=[('AF', 'Afghanistan'), ('AX', 'Åland Islands'), ('AL', 'Albania'), ('DZ', 'Algeria'), ('AS', 'American Samoa'), ('AD', 'Andorra'), ('AO', 'Angola'), ('AI', 'Anguilla'), ('AQ', 'Antarctica'), ('AG', 'Antigua and Barbuda'), ('AR', 'Argentina'), ('AM', 'Armenia'), ('AW', 'Aruba'), ('AU', 'Australia'), ('AT', 'Austria'), ('AZ', 'Azerbaijan'), ('BS', 'Bahamas'), ('BH', 'Bahrain'), ('BD', 'Bangladesh'), ('BB', 'Barbados'), ('BY', 'Belarus'), ('BE', 'Belgium'), ('BZ', 'Belize'), ('BJ', 'Benin'), ('BM', 'Bermuda'), ('BT', 'Bhutan'), ('BO', 'Bolivia, Plurinational State of'), ('BQ', 'Bonaire, Sint Eustatius and Saba'), ('BA', 'Bosnia and Herzegovina'), ('BW', 'Botswana'), ('BV', 'Bouvet Island'), ('BR', 'Brazil'), ('IO', 'British Indian Ocean Territory'), ('BN', 'Brunei Darussalam'), ('BG', 'Bulgaria'), ('BF', 'Burkina Faso'), ('BI', 'Burundi'), ('KH', 'Cambodia'), ('CM', 'Cameroon'), ('CA', 'Canada'), ('CV', 'Cape Verde'), ('KY', 'Cayman Islands'), ('CF', 'Central African Republic'), ('TD', 'Chad'), ('CL', 'Chile'), ('CN', 'China'), ('CX', 'Christmas Island'), ('CC', 'Cocos (Keeling) Islands'), ('CO', 'Colombia'), ('KM', 'Comoros'), ('CG', 'Congo'), ('CD', 'Congo, the Democratic Republic of the'), ('CK', 'Cook Islands'), ('CR', 'Costa Rica'), ('CI', "Côte d'Ivoire"), ('HR', 'Croatia'), ('CU', 'Cuba'), ('CW', 'Curaçao'), ('CY', 'Cyprus'), ('CZ', 'Czech Republic'), ('DK', 'Denmark'), ('DJ', 'Djibouti'), ('DM', 'Dominica'), ('DO', 'Dominican Republic'), ('EC', 'Ecuador'), ('EG', 'Egypt'), ('SV', 'El Salvador'), ('GQ', 'Equatorial Guinea'), ('ER', 'Eritrea'), ('EE', 'Estonia'), ('ET', 'Ethiopia'), ('FK', 'Falkland Islands (Malvinas)'), ('FO', 'Faroe Islands'), ('FJ', 'Fiji'), ('FI', 'Finland'), ('FR', 'France'), ('GF', 'French Guiana'), ('PF', 'French Polynesia'), ('TF', 'French Southern Territories'), ('GA', 'Gabon'), ('GM', 'Gambia'), ('GE', 'Georgia'), ('DE', 'Germany'), ('GH', 'Ghana'), ('GI', 'Gibraltar'), ('GR', 'Greece'), ('GL', 'Greenland'), ('GD', 'Grenada'), ('GP', 'Guadeloupe'), ('GU', 'Guam'), ('GT', 'Guatemala'), ('GG', 'Guernsey'), ('GN', 'Guinea'), ('GW', 'Guinea-Bissau'), ('GY', 'Guyana'), ('HT', 'Haiti'), ('HM', 'Heard Island and McDonald Islands'), ('VA', 'Holy See (Vatican City State)'), ('HN', 'Honduras'), ('HK', 'Hong Kong'), ('HU', 'Hungary'), ('IS', 'Iceland'), ('IN', 'India'), ('ID', 'Indonesia'), ('IR', 'Iran, Islamic Republic of'), ('IQ', 'Iraq'), ('IE', 'Ireland'), ('IM', 'Isle of Man'), ('IL', 'Israel'), ('IT', 'Italy'), ('JM', 'Jamaica'), ('JP', 'Japan'), ('JE', 'Jersey'), ('JO', 'Jordan'), ('KZ', 'Kazakhstan'), ('KE', 'Kenya'), ('KI', 'Kiribati'), ('KP', "Korea, Democratic People's Republic of"), ('KR', 'Korea, Republic of'), ('KW', 'Kuwait'), ('KG', 'Kyrgyzstan'), ('LA', "Lao People's Democratic Republic"), ('LV', 'Latvia'), ('LB', 'Lebanon'), ('LS', 'Lesotho'), ('LR', 'Liberia'), ('LY', 'Libya'), ('LI', 'Liechtenstein'), ('LT', 'Lithuania'), ('LU', 'Luxembourg'), ('MO', 'Macao'), ('MK', 'Macedonia, the Former Yugoslav Republic of'), ('MG', 'Madagascar'), ('MW', 'Malawi'), ('MY', 'Malaysia'), ('MV', 'Maldives'), ('ML', 'Mali'), ('MT', 'Malta'), ('MH', 'Marshall Islands'), ('MQ', 'Martinique'), ('MR', 'Mauritania'), ('MU', 'Mauritius'), ('YT', 'Mayotte'), ('MX', 'Mexico'), ('FM', 'Micronesia, Federated States of'), ('MD', 'Moldova, Republic of'), ('MC', 'Monaco'), ('MN', 'Mongolia'), ('ME', 'Montenegro'), ('MS', 'Montserrat'), ('MA', 'Morocco'), ('MZ', 'Mozambique'), ('MM', 'Myanmar'), ('NA', 'Namibia'), ('NR', 'Nauru'), ('NP', 'Nepal'), ('NL', 'Netherlands'), ('NC', 'New Caledonia'), ('NZ', 'New Zealand'), ('NI', 'Nicaragua'), ('NE', 'Niger'), ('NG', 'Nigeria'), ('NU', 'Niue'), ('NF', 'Norfolk Island'), ('MP', 'Northern Mariana Islands'), ('NO', 'Norway'), ('OM', 'Oman'), ('PK', 'Pakistan'), ('PW', 'Palau'), ('PS', 'Palestine, State of'), ('PA', 'Panama'), ('PG', 'Papua New Guinea'), ('PY', 'Paraguay'), ('PE', 'Peru'), ('PH', 'Philippines'), ('PN', 'Pitcairn'), ('PL', 'Poland'), ('PT', 'Portugal'), ('PR', 'Puerto Rico'), ('QA', 'Qatar'), ('RE', 'Réunion'), ('RO', 'Romania'), ('RU', 'Russian Federation'), ('RW', 'Rwanda'), ('BL', 'Saint Barthélemy'), ('SH', 'Saint Helena, Ascension and Tristan da Cunha'), ('KN', 'Saint Kitts and Nevis'), ('LC', 'Saint Lucia'), ('MF', 'Saint Martin (French part)'), ('PM', 'Saint Pierre and Miquelon'), ('VC', 'Saint Vincent and the Grenadines'), ('WS', 'Samoa'), ('SM', 'San Marino'), ('ST', 'Sao Tome and Principe'), ('SA', 'Saudi Arabia'), ('SN', 'Senegal'), ('RS', 'Serbia'), ('SC', 'Seychelles'), ('SL', 'Sierra Leone'), ('SG', 'Singapore'), ('SX', 'Sint Maarten (Dutch part)'), ('SK', 'Slovakia'), ('SI', 'Slovenia'), ('SB', 'Solomon Islands'), ('SO', 'Somalia'), ('ZA', 'South Africa'), ('GS', 'South Georgia and the South Sandwich Islands'), ('SS', 'South Sudan'), ('ES', 'Spain'), ('LK', 'Sri Lanka'), ('SD', 'Sudan'), ('SR', 'Suriname'), ('SJ', 'Svalbard and Jan Mayen'), ('SZ', 'Swaziland'), ('SE', 'Sweden'), ('CH', 'Switzerland'), ('SY', 'Syrian Arab Republic'), ('TW', 'Taiwan, Province of China'), ('TJ', 'Tajikistan'), ('TZ', 'Tanzania, United Republic of'), ('TH', 'Thailand'), ('TL', 'Timor-Leste'), ('TG', 'Togo'), ('TK', 'Tokelau'), ('TO', 'Tonga'), ('TT', 'Trinidad and Tobago'), ('TN', 'Tunisia'), ('TR', 'Turkey'), ('TM', 'Turkmenistan'), ('TC', 'Turks and Caicos Islands'), ('TV', 'Tuvalu'), ('UG', 'Uganda'), ('UA', 'Ukraine'), ('AE', 'United Arab Emirates'), ('GB', 'United Kingdom'), ('US', 'United States'), ('UM', 'United States Minor Outlying Islands'), ('UY', 'Uruguay'), ('UZ', 'Uzbekistan'), ('VU', 'Vanuatu'), ('VE', 'Venezuela, Bolivarian Republic of'), ('VN', 'Viet Nam'), ('VG', 'Virgin Islands, British'), ('VI', 'Virgin Islands, U.S.'), ('WF', 'Wallis and Futuna'), ('EH', 'Western Sahara'), ('YE', 'Yemen'), ('ZM', 'Zambia'), ('ZW', 'Zimbabwe')], help_text="The school's country.", null=True, verbose_name='country')),
                ('uk_county', models.TextField(blank=True, choices=[('Aberdeen City', 'Aberdeen City'), ('Aberdeenshire', 'Aberdeenshire'), ('Angus', 'Angus'), ('Argyll and Bute', 'Argyll and Bute'), ('Bedfordshire', 'Bedfordshire'), ('Belfast', 'Belfast'), ('Belfast Greater', 'Belfast Greater'), ('Berkshire', 'Berkshire'), ('Blaenau Gwent', 'Blaenau Gwent'), ('Bridgend', 'Bridgend'), ('Buckinghamshire', 'Buckinghamshire'), ('Caerphilly', 'Caerphilly'), ('Cambridgeshire', 'Cambridgeshire'), ('Cardiff', 'Cardiff'), ('Carmarthenshire', 'Carmarthenshire'), ('Ceredigion', 'Ceredigion'), ('Channel Islands', 'Channel Islands'), ('Cheshire', 'Cheshire'), ('City of Edinburgh', 'City of Edinburgh'), ('Clackmannanshire', 'Clackmannanshire'), ('Conwy', 'Conwy'), ('Cornwall', 'Cornwall'), ('County Antrim', 'County Antrim'), ('County Armagh', 'County Armagh'), ('County Down', 'County Down'), ('County Fermanagh', 'County Fermanagh'), ('County Londonderry', 'County Londonderry'), ('County Tyrone', 'County Tyrone'), ('County of Bristol', 'County of Bristol'), ('Cumbria', 'Cumbria'), ('Denbighshire', 'Denbighshire'), ('Derbyshire', 'Derbyshire'), ('Devon', 'Devon'), ('Dorset', 'Dorset'), ('Dumfries and Galloway', 'Dumfries and Galloway'), ('Dunbartonshire', 'Dunbartonshire'), ('Dundee City', 'Dundee City'), ('Durham', 'Durham'), ('East Ayrshire', 'East Ayrshire'), ('East Dunbartonshire', 'East Dunbartonshire'), ('East Lothian', 'East Lothian'), ('East Renfrewshire', 'East Renfrewshire'), ('East Riding of Yorkshire', 'East Riding of Yorkshire'), ('East Sussex', 'East Sussex'), ('Essex', 'Essex'), ('Falkirk', 'Falkirk'), ('Fife', 'Fife'), ('Flintshire', 'Flintshire'), ('Glasgow City', 'Glasgow City'), ('Gloucestershire', 'Gloucestershire'), ('Greater London', 'Greater London'), ('Greater Manchester', 'Greater Manchester'), ('Guernsey Channel Islands', 'Guernsey Channel Islands'), ('Gwynedd', 'Gwynedd'), ('Hampshire', 'Hampshire'), ('Hereford and Worcester', 'Hereford and Worcester'), ('Herefordshire', 'Herefordshire'), ('Hertfordshire', 'Hertfordshire'), ('Highland', 'Highland'), ('Inverclyde', 'Inverclyde'), ('Inverness', 'Inverness'), ('Isle of Anglesey', 'Isle of Anglesey'), ('Isle of Barra', 'Isle of Barra'), ('Isle of Man', 'Isle of Man'), ('Isle of Wight', 'Isle of Wight'), ('Jersey Channel Islands', 'Jersey Channel Islands'), ('Kent', 'Kent'), ('Lancashire', 'Lancashire'), ('Leicestershire', 'Leicestershire'), ('Lincolnshire', 'Lincolnshire'), ('Merseyside', 'Merseyside'), ('Merthyr Tydfil', 'Merthyr Tydfil'), ('Midlothian', 'Midlothian'), ('Monmouthshire', 'Monmouthshire'), ('Moray', 'Moray'), ('Neath Port Talbot', 'Neath Port Talbot'), ('Newport', 'Newport'), ('Norfolk', 'Norfolk'), ('North Ayrshire', 'North Ayrshire'), ('North Lanarkshire', 'North Lanarkshire'), ('North Yorkshire', 'North Yorkshire'), ('Northamptonshire', 'Northamptonshire'), ('Northumberland', 'Northumberland'), ('Nottinghamshire', 'Nottinghamshire'), ('Orkney', 'Orkney'), ('Orkney Islands', 'Orkney Islands'), ('Oxfordshire', 'Oxfordshire'), ('Pembrokeshire', 'Pembrokeshire'), ('Perth and Kinross', 'Perth and Kinross'), ('Powys', 'Powys'), ('Renfrewshire', 'Renfrewshire'), ('Rhondda Cynon Taff', 'Rhondda Cynon Taff'), ('Rutland', 'Rutland'), ('Scottish Borders', 'Scottish Borders'), ('Shetland Islands', 'Shetland Islands'), ('Shropshire', 'Shropshire'), ('Somerset', 'Somerset'), ('South Ayrshire', 'South Ayrshire'), ('South Lanarkshire', 'South Lanarkshire'), ('South Yorkshire', 'South Yorkshire'), ('Staffordshire', 'Staffordshire'), ('Stirling', 'Stirling'), ('Suffolk', 'Suffolk'), ('Surrey', 'Surrey'), ('Swansea', 'Swansea'), ('Torfaen', 'Torfaen'), ('Tyne and Wear', 'Tyne and Wear'), ('Vale of Glamorgan', 'Vale of Glamorgan'), ('Warwickshire', 'Warwickshire'), ('West Dunbart', 'West Dunbart'), ('West Lothian', 'West Lothian'), ('West Midlands', 'West Midlands'), ('West Sussex', 'West Sussex'), ('West Yorkshire', 'West Yorkshire'), ('Western Isles', 'Western Isles'), ('Wiltshire', 'Wiltshire'), ('Worcestershire', 'Worcestershire'), ('Wrexham', 'Wrexham')], help_text="The school's county within the United Kingdom. This value may only be set if the school's country is set to UK.", null=True, verbose_name='united kingdom county')),
            ],
            options={
                'verbose_name': 'school',
                'verbose_name_plural': 'schools',
            },
        ),
        migrations.CreateModel(
            name='Session',
            fields=[
                ('session_key', models.CharField(max_length=40, primary_key=True, serialize=False, verbose_name='session key')),
                ('session_data', models.TextField(verbose_name='session data')),
                ('expire_date', models.DateTimeField(db_index=True, verbose_name='expire date')),
                ('user', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'session',
                'verbose_name_plural': 'sessions',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Teacher',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_saved_at', models.DateTimeField(auto_now=True, help_text='Record the last time the model was saved. This is used by our data warehouse to know what data was modified since the last scheduled data transfer from the database to the data warehouse.', verbose_name='last saved at')),
                ('delete_after', models.DateTimeField(blank=True, help_text="When this data is scheduled for deletion. Set to null if not scheduled for deletion. This is used by our data warehouse to transfer data that's been scheduled for deletion before it's actually deleted. Data will actually be deleted in a CRON job after this point in time.", null=True, verbose_name='delete after')),
                ('is_admin', models.BooleanField(default=False, help_text='Designates if the teacher has admin privileges.', verbose_name='is administrator')),
                ('school', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='teachers', to='user.school')),
            ],
            options={
                'verbose_name': 'teacher',
                'verbose_name_plural': 'teachers',
            },
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_saved_at', models.DateTimeField(auto_now=True, help_text='Record the last time the model was saved. This is used by our data warehouse to know what data was modified since the last scheduled data transfer from the database to the data warehouse.', verbose_name='last saved at')),
                ('delete_after', models.DateTimeField(blank=True, help_text="When this data is scheduled for deletion. Set to null if not scheduled for deletion. This is used by our data warehouse to transfer data that's been scheduled for deletion before it's actually deleted. Data will actually be deleted in a CRON job after this point in time.", null=True, verbose_name='delete after')),
                ('auto_gen_password', models.CharField(editable=False, help_text='An auto-generated password that allows student to log directly into their account.', max_length=64, validators=[django.core.validators.MinLengthValidator(64)], verbose_name='automatically generated password')),
                ('klass', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='students', to='user.class')),
                ('school', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='students', to='user.school')),
            ],
            options={
                'verbose_name': 'student',
                'verbose_name_plural': 'students',
            },
        ),
        migrations.CreateModel(
            name='SessionAuthFactor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('auth_factor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='session_auth_factors', to='user.authfactor')),
                ('session', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='session_auth_factors', to='user.session')),
            ],
            options={
                'verbose_name': 'session auth factor',
                'verbose_name_plural': 'session auth factors',
            },
        ),
        migrations.AddConstraint(
            model_name='school',
            constraint=models.CheckConstraint(check=models.Q(('uk_county__isnull', True), ('country', 'GB'), _connector='OR'), name='school__no_uk_county_if_country_not_uk'),
        ),
        migrations.AddField(
            model_name='otpbypasstoken',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='otp_bypass_tokens', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='class',
            name='school',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='classes', to='user.school'),
        ),
        migrations.AddField(
            model_name='class',
            name='teacher',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='classes', to='user.teacher'),
        ),
        migrations.AddField(
            model_name='authfactor',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='auth_factors', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='user',
            name='groups',
            field=models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups'),
        ),
        migrations.AddField(
            model_name='user',
            name='student',
            field=models.OneToOneField(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, to='user.student'),
        ),
        migrations.AddField(
            model_name='user',
            name='teacher',
            field=models.OneToOneField(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, to='user.teacher'),
        ),
        migrations.AddField(
            model_name='user',
            name='user_permissions',
            field=models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions'),
        ),
        migrations.AlterUniqueTogether(
            name='sessionauthfactor',
            unique_together={('session', 'auth_factor')},
        ),
        migrations.AlterUniqueTogether(
            name='otpbypasstoken',
            unique_together={('user', 'token')},
        ),
        migrations.AlterUniqueTogether(
            name='class',
            unique_together={('name', 'school')},
        ),
        migrations.AlterUniqueTogether(
            name='authfactor',
            unique_together={('user', 'type')},
        ),
        migrations.AddConstraint(
            model_name='user',
            constraint=models.CheckConstraint(check=models.Q(('student__isnull', False), ('teacher__isnull', False), _negated=True), name='user__profile'),
        ),
        migrations.AddConstraint(
            model_name='user',
            constraint=models.CheckConstraint(check=models.Q(models.Q(('email__isnull', False), ('teacher__isnull', False)), models.Q(('email__isnull', True), ('student__isnull', False)), models.Q(('email__isnull', False), ('student__isnull', True), ('teacher__isnull', True)), _connector='OR'), name='user__email'),
        ),
        migrations.AddConstraint(
            model_name='user',
            constraint=models.CheckConstraint(check=models.Q(models.Q(('last_name__isnull', False), ('teacher__isnull', False)), models.Q(('last_name__isnull', True), ('student__isnull', False)), models.Q(('last_name__isnull', False), ('student__isnull', True), ('teacher__isnull', True)), _connector='OR'), name='user__last_name'),
        ),
    ]
