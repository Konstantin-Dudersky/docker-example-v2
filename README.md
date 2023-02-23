# docker-example

Пример организации проекта с docker-образами.

## Рабочий процесс

2 машины:

- ==dev== - машина разработчика
- ==target== - целевая машина

Чтобы не задавать ip-адреса в скриптах, пропишем домены в файле `/etc/hosts`.

На ==dev==:

```
__IP_TARGET__    target
127.0.0.1        docker-registry
```

На ==target==:

```
127.0.0.1     target
__IP_DEV__    docker-registry
```

Порядок работы:

- образы собираются на машине ==dev== и сохраняются в репозитории на этой же машине. Образы собираются с тегом `docker-registry:5000`.
- (опционально) образы можно сохранить в файлы tar или загрузить из tar
- при запуске `docker compose` на целевой машине скачиваюся образы из репозитория `docker-registry:5000`.

## Запуск локального репозитория образов ==dev==

Развернем локальный репозиторий образов вместе с веб-интерфейсом.

### Установка

Клонируем репозиторий:

```sh
cd ~/snap && mkdir docker-registry
```

Создадим файлы. Файл конфигурации хранилища образов `docker-registry-config.yml`:

```yaml
version: 0.1
log:
  fields:
    service: registry
storage:
  delete:
    enabled: true
  cache:
    blobdescriptor: inmemory
  filesystem:
    rootdirectory: /var/lib/registry
http:
  addr: :5000
  headers:
    X-Content-Type-Options: [nosniff]
    Access-Control-Allow-Origin: ['*']
    Access-Control-Allow-Methods: ['HEAD', 'GET', 'OPTIONS', 'DELETE']
    Access-Control-Allow-Headers: ['Authorization', 'Accept', 'Cache-Control']
    Access-Control-Expose-Headers: ['Docker-Content-Digest']
```

Файл для запуска хранилища и веб-интерфейса `docker-compose.yml`:

```yaml
version: '2.0'
name: docker-registry

services:
  registry:
    image: registry:2.8
    container_name: docker-registry
    ports:
      - 5000:5000
    volumes:
      - ./registry-data:/var/lib/registry
      - ./docker-registry-config.yml:/etc/docker/registry/config.yml

  ui:
    image: joxit/docker-registry-ui:latest
    container_name: docker-registry-ui
    ports:
      - 8000:80
    environment:
      - REGISTRY_TITLE=My Private Docker Registry
      - REGISTRY_URL=http://docker-registry:5000
      - SINGLE_REGISTRY=true
      - THEME=dark
    depends_on:
      - registry
```

### Запуск

Запускать командой:

```sh
cd ~/snap/docker-registry \
	&& docker compose up -d
```

- Репозиторий образов доступен по адресу: http://docker-registry:5000

- Веб-интерфейс доступен по адресу: http://docker-registry:8000

## Создание билдера buildx ==dev==

Локальный репозиторий образов, для простоты, работает по протоколу http. Чтобы билдер смог загрузить образы, необходимо задать конфигурацию (выполнить в терминале одной строкой):

```sh
test -f ~/.buildkitd.toml || echo \
'[registry."docker-registry:5000"]
http = true
insecure = true' \
> ~/.buildkitd.toml
```

Создать билдер можно командой:

```sh
docker buildx rm builder \
; docker run --rm --privileged multiarch/qemu-user-static --reset -p yes \
&& docker buildx create --name builder --driver docker-container --use --driver-opt network=host --config ~/.buildkitd.toml \
&& docker buildx inspect --bootstrap
```

## Разрешить загрузку образов по протоколу http ==dev==, ==target==

На всех машинах в файле `/etc/docker/daemon.json`:

```json
{ "insecure-registries":["docker-registry:5000"] }
```

После перезагрузить сервис docker:

```bash
sudo systemctl daemon-reload && sudo systemctl restart docker
```

## Сборка образов ==dev==

Сборка образов описывается в файле `docker-bake.hcl`.

Запуск сборки:

```sh
docker buildx bake --builder builder -f docker-bake.hcl --push service_group
```

При сборке образы загружаются в локальный репозиторий `docker-registry:5000`. Возможна мультиплатформенная сборка.

## Скачивание образов на целевой машине из репозитория ==target==

Копируем код на целевую машину. Скачиваем образы:

```bash
docker compose --profile server --profile system pull
```

## Запуск сервисов на целевой машине ==target==

Запускаем командой:

```sh
docker compose --profile server up -d
```

Останавливаем:

```sh
docker compose --profile server down
```

- Сохранение образов из локального репозитория в tar-файлы.
