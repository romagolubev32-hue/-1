from django.core.management.base import BaseCommand

from core.models import Project, Skill, User


class Command(BaseCommand):
    help = "Создает тестовых пользователей, навыки и проекты"

    def handle(self, *args, **options):
        skills_map = {}
        skill_names = [
            "Python",
            "Django",
            "JavaScript",
            "React",
            "PostgreSQL",
            "HTML",
            "CSS",
            "C++",
            "C#",
            "Figma",
        ]

        for name in skill_names:
            skill, _ = Skill.objects.get_or_create(name=name)
            skills_map[name] = skill

        users_data = [
            {
                "email": "alex@example.com",
                "first_name": "Алексей",
                "last_name": "Иванов",
                "about": "Backend-разработчик, люблю Django и PostgreSQL",
                "phone": "+7 (999) 111-11-11",
                "github_url": "https://github.com/alexivanov",
                "password": "testpass123",
                "skills": ["Python", "Django", "PostgreSQL"],
            },
            {
                "email": "maria@example.com",
                "first_name": "Мария",
                "last_name": "Петрова",
                "about": "Frontend-разработчик, работаю с React и JavaScript",
                "phone": "+7 (999) 222-22-22",
                "github_url": "https://github.com/mariapetrova",
                "password": "testpass123",
                "skills": ["JavaScript", "React", "HTML", "CSS"],
            },
            {
                "email": "ivan@example.com",
                "first_name": "Иван",
                "last_name": "Сидоров",
                "about": "Fullstack-разработчик, интересуюсь pet-проектами",
                "phone": "+7 (999) 333-33-33",
                "github_url": "https://github.com/ivansidorov",
                "password": "testpass123",
                "skills": ["Python", "JavaScript", "PostgreSQL"],
            },
            {
                "email": "olga@example.com",
                "first_name": "Ольга",
                "last_name": "Козлова",
                "about": "UI/UX дизайнер, люблю Figma и красивые интерфейсы",
                "phone": "+7 (999) 444-44-44",
                "github_url": "https://github.com/olgakozlova",
                "password": "testpass123",
                "skills": ["Figma", "HTML", "CSS"],
            },
            {
                "email": "nikita@example.com",
                "first_name": "Никита",
                "last_name": "Смирнов",
                "about": "Разработчик на C++ и C#, ищу команду для интересных идей",
                "phone": "+7 (999) 555-55-55",
                "github_url": "https://github.com/nikitasmirnov",
                "password": "testpass123",
                "skills": ["C++", "C#"],
            },
        ]

        created_users = {}

        for user_data in users_data:
            email = user_data["email"]
            password = user_data.pop("password")
            skill_list = user_data.pop("skills")

            user, created = User.objects.get_or_create(
                email=email,
                defaults=user_data,
            )

            if created:
                user.set_password(password)
                user.save()
                self.stdout.write(self.style.SUCCESS(f"Создан пользователь: {email}"))
            else:
                self.stdout.write(f"Пользователь уже существует: {email}")

            for skill_name in skill_list:
                user.skills.add(skills_map[skill_name])

            created_users[email] = user

        projects_data = [
            {
                "owner_email": "alex@example.com",
                "name": "Сервис поиска команды",
                "description": "Платформа для поиска разработчиков и дизайнеров в pet-проекты.",
                "github_url": "https://github.com/alexivanov/team-finder-demo",
                "status": Project.STATUS_OPEN,
                "participants": ["maria@example.com", "ivan@example.com"],
            },
            {
                "owner_email": "maria@example.com",
                "name": "Трекер привычек",
                "description": "Приложение для отслеживания привычек и прогресса.",
                "github_url": "https://github.com/mariapetrova/habit-tracker",
                "status": Project.STATUS_OPEN,
                "participants": ["alex@example.com"],
            },
            {
                "owner_email": "ivan@example.com",
                "name": "Планировщик задач",
                "description": "Веб-приложение для командного управления задачами.",
                "github_url": "https://github.com/ivansidorov/task-planner",
                "status": Project.STATUS_OPEN,
                "participants": ["olga@example.com"],
            },
            {
                "owner_email": "olga@example.com",
                "name": "Дизайн-система для стартапа",
                "description": "Набор UI-компонентов и дизайн-гайд для веб-сервиса.",
                "github_url": "https://github.com/olgakozlova/design-system",
                "status": Project.STATUS_CLOSED,
                "participants": ["maria@example.com"],
            },
            {
                "owner_email": "nikita@example.com",
                "name": "Десктопное приложение для учета расходов",
                "description": "Приложение на C# для ведения личных финансов.",
                "github_url": "https://github.com/nikitasmirnov/finance-app",
                "status": Project.STATUS_OPEN,
                "participants": ["ivan@example.com"],
            },
        ]

        for project_data in projects_data:
            owner = created_users[project_data["owner_email"]]
            participants_emails = project_data.pop("participants")
            project_name = project_data["name"]

            project, created = Project.objects.get_or_create(
                owner=owner,
                name=project_name,
                defaults={
                    "description": project_data["description"],
                    "github_url": project_data["github_url"],
                    "status": project_data["status"],
                },
            )

            if created:
                self.stdout.write(self.style.SUCCESS(f"Создан проект: {project.name}"))
            else:
                self.stdout.write(f"Проект уже существует: {project.name}")

            for email in participants_emails:
                participant = created_users[email]
                if participant != owner:
                    project.participants.add(participant)

        self.stdout.write(self.style.SUCCESS("Тестовые данные успешно загружены."))