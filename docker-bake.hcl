/*
Запустить сборку и загрузку образов:

docker buildx bake --builder builder -f docker-bake.hcl --push service_group
*/

PYTHON_VER = "3.11.2"
POETRY_VER = "1.3.2"
NGINX_VER = "1.23"

REPO = "docker-registry:5000"

PLATFORMS = [
    "linux/amd64",
    "linux/arm64",
]

target "webapp" {
    dockerfile = "webapp/Dockerfile"
    args = {
        NGINX_VER = "${NGINX_VER}"
    }
    tags = [ "${REPO}/docker-example/webapp" ]
    platforms = PLATFORMS
}

# базовый образ для сервисов python
target "base_python_image" {
    dockerfile = "shared/Dockerfile"
    args = {
        POETRY_VER = "${POETRY_VER}",
        PYTHON_VER = "${PYTHON_VER}",
    }
    platforms = PLATFORMS
}


target "python_service" {
    contexts = {
        base_image = "target:base_python_image"
    }
    dockerfile = "python_service/Dockerfile"
    tags = [ "${REPO}/docker-example/python_service" ]
    platforms = PLATFORMS
}


group "service_group" {
    targets = [
        "python_service",
        "webapp",
    ]
}
