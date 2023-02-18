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
cd ~/snap \
	&& git clone https://github.com/Joxit/docker-registry-ui.git
```

Настроим веб-интерфейс для работы через порт 8000.

- в файле `~/snap/docker-registry-ui/examples/ui-as-standalone/registry-config/simple.yml` поменять заголовок:

```yml
Access-Control-Allow-Origin: ["*"]
```

- поменять порт для сервиса `ui` в файле `~/snap/docker-registry-ui/examples/ui-as-standalone/simple.yml`

```yml
ports:
	8000:80
```

### Запуск

Запускать командой:

```sh
cd ~/snap/docker-registry-ui/examples/ui-as-standalone \
	&& docker compose -f simple.yml up -d
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
