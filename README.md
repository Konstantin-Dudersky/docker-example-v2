# docker-example

Пример организации проекта с docker-образами.

## Рабочий процесс

2 машины:

- ==localhost== - машина разработчика
- ==target== - целевая машина

Чтобы не задавать ip-адреса в скриптах, пропишем домены в файле /etc/hosts.

На ==localhost==:

```
__IP__        target
```

На ==target==:

```
127.0.0.1     target
```

Порядок работы:

- образы собираются на машине ==localhost== и сохраняются в репозитории на этой же машине. Образы собираются с тегом `localhost:5000`.
- (опционально) образы можно сохранить в файлы tar или загрузить из tar
- добавляем к образам тег - вместо `localhost:5000` заменяем `target:5000`
- перемещаем образы в репозиторий на машине ==target==.
- при запуске `docker compose` на целевой машине скачиваюся образы из репозитория `target:5000`.

## Запуск локального репозитория образов ==localhost==

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

- Репозиторий образов доступен по адресу: http://localhost:5000

- Веб-интерфейс доступен по адресу: http://localhost:8000

## Создание билдера buildx

Локальный репозиторий образов, для простоты, работает по протоколу http. Чтобы билдер смог загрузить образы, необходимо задать конфигурацию (выполнить в терминале одной строкой):

```sh
test -f ~/.buildkitd.toml || echo \
'[registry."localhost:5000"]
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

## Сборка образов

Сборка образов описывается в файле `docker-bake.hcl`.

Запуск сборки:

```sh
docker buildx bake --builder builder -f docker-bake.hcl --push service_group
```

При сборке образы загружаются в локальный репозиторий `localhost:5000`. Возможна мультиплатформенная сборка.

## Запуск репозитория образов на целевой машине ==target==

На целевой также необходим репозиторий образов. В файле `docker-compose.yml` в профиле `system` перечислены несколько сервисов:

- docker_registry - репозиторий образов, порт 5000
- docker_registry_ui - веб-интерфейс для репозитория, порт 8000, протокол http
- portainer - мониторинг образов, порт 8001, протокол http

У сервисов указан `restart: always`, т.е. контейнеры будут автоматически запускаться при перезагрузке машины.

Запускаем командой:

```sh
docker compose --profile system up -d
```

## Перемещение образов из локального репозитория на целевую машину

Перемещение происходит в несколько этапов:

- Загружаем образ из локального репозитория
- Меняем в теге адрес репозитория, ставим целевой (`target:5000`)
- Выгружаем образы в репозиторий на целевой машине

В файле `docker_compose_tasks.py` приведен пример скрипта, который выполняет все эти задачи.

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
