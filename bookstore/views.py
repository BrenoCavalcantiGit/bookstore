from pathlib import Path

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt


def get_last_commit():
    """Devolve o último commit do repositório (ou None se não for possível ler)."""
    try:
        import git

        commit = git.Repo(settings.BASE_DIR).head.commit
        return {
            'sha': commit.hexsha[:7],
            'message': commit.message.strip().splitlines()[0],
        }
    except Exception:
        return None


def hello(request):
    return render(request, 'hello_world.html', {'commit': get_last_commit()})


@csrf_exempt
def update(request):
    """Recebe o webhook do GitHub, atualiza o código e recarrega o site."""
    if request.method != 'POST':
        return HttpResponse('Método não permitido', status=405)

    try:
        import git

        repo = git.Repo(settings.BASE_DIR)
        repo.remotes.origin.pull()
    except Exception as error:
        return HttpResponse(f'Erro ao atualizar o código: {error}', status=500)

    # No PythonAnywhere, "tocar" no arquivo WSGI recarrega o site
    wsgi_name = settings.PYTHONANYWHERE_DOMAIN.replace('.', '_') + '_wsgi.py'
    wsgi_file = Path('/var/www') / wsgi_name
    if wsgi_file.exists():
        wsgi_file.touch()

    return HttpResponse('Código atualizado no PythonAnywhere')
