$rootDir = git rev-parse --show-toplevel
$project_path = Read-Host "Enter project path:"
$rootDir = Join-Path -Path $rootDir -ChildPath $project_path

isort --sp=pyproject.toml $rootDir
black --config pyproject.toml $rootDir
pylint --rcfile=pyproject.toml $rootDir