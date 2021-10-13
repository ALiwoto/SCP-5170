import httpx
import ujson as json
from scp.plugins.user.reporting import report_error
from scp.utils.strUtils import remove_prefix
from scp import user

__PLUGIN__ = 'follow'
__DOC__ = str(
    user.md.KanTeXDocument(
        user.md.Section(
            'HTTP(s) Tools',
            user.md.SubSection(
                'Redirect',
                user.md.Code('(*prefix)url {url}'),
            ),
            user.md.SubSection(
                'IpInfo',
                user.md.Code('(*prefix)dns {ip_address} - * optional'),
            ),
            user.md.SubSection(
                'urls',
                user.md.Code('(*prefix)urls {url} - * optional'),
            ),
        ),
    ),
)


@user.on_message(user.sudo & user.command('url'))
async def _(_, message: user.types.Message):
    if len(message.command) == 1:
        return await message.delete()
    link = message.command[1]
    text = user.md.KanTeXDocument(
        user.md.Section(
            'Redirect',
            user.md.KeyValueItem(
                user.md.Bold('Original URL'), user.md.Code(link),
            ),
            user.md.KeyValueItem(
                user.md.Bold('Followed URL'),
                user.md.Code(await user.resolve_url(link)),
            ),
        ),
    )
    await message.reply(text, quote=True)


@user.on_message(user.filters.me & user.command('dns'))
async def _(_, message: user.types.Message):
    query = '' if len(message.command) == 1 else message.command[1]
    doc = user.md.KanTeXDocument()
    sec = user.md.Section(f'IP-info: `{query}`')
    for key, value in (
        await user.Request('http://ip-api.com/json/' + query, type='get')
    ).items():
        sec.append(
            user.md.KeyValueItem(
                user.md.Bold(key), user.md.Code(value),
            ),
        )
    doc.append(sec)
    await message.reply(doc, quote=True)


@user.on_message(user.sudo & user.command('urls'))
async def cssworker_urls(_, message: user.types.Message):
    msg = message.text
    the_url = msg.split(" ", 1)
    wrong = False

    if len(the_url) == 1:
        if message.reply_to_message:
            msg = message.reply_to_message.text
            the_url = msg
        else:
            wrong = True
    else:
        the_url = the_url[1]

    if wrong:
        return

    try:
        res_json = await url_cssworker(target_url=the_url)
    except BaseException as e:
        await report_error(e, "urls", message.from_user)
        return

    if res_json:
        # {"url":"image_url","response_time":"147ms"}
        image_url = res_json["url"]
        if image_url:
            await message.reply_photo(image_url)
        else:
            await report_error("couldn't get url value, most probably API is not accessible.",
                "urls", message.from_user)

    else:
        await report_error("Failed, because API is not responding, try it later.",
                "urls", message.from_user)

    return


@user.on_message(user.sudo & user.command('html'))
async def cssworker_html(_, message: user.types.Message):
    msg = message.text
    the_html = msg.split(" ", 1)
    wrong = False

    if len(the_html) == 1:
        if message.reply_to_message:
            msg = message.reply_to_message.text
            the_html = msg
            if len(the_html) == 1:
                wrong = True
            else:
                the_html = the_html[1]
        else:
            wrong = True
    else:
        the_html = the_html[1]

    if wrong:
        #await message.reply_text("Format : [!, /]html < your html code > (or reply to a message")
        return


    try:
        res_json = await html_cssworker(target_html=the_html)
    except BaseException as e:
        await report_error(e, "urls", message.from_user)
        return

    if res_json:
        image_url = res_json["url"]
        if image_url:
            await message.reply_photo(image_url)
        else:
            await report_error("couldn't get url value, most probably API is not accessible.",
                "urls", message.from_user)
    else:
        await report_error("Failed, because API is not responding, try it later.",
                "urls", message.from_user)

    return




async def url_cssworker(target_url: str):
    url = "https://htmlcsstoimage.com/demo_run"
    my_headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0',
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': 'https://htmlcsstoimage.com/',
        'Content-Type': 'application/json',
        'Origin': 'https://htmlcsstoimage.com',
        'Alt-Used': 'htmlcsstoimage.com',
        'Connection': 'keep-alive',
    }

    # remove 'https' prefixes to avoid bugging out api
    target_url = remove_prefix(target_url, "https://")
    target_url = remove_prefix(target_url, "http://")

    data = json.dumps({"html": "", "console_mode": "", "url": target_url, "css": "", "selector": "", "ms_delay": "",
                        "render_when_ready": "false", "viewport_height": "", "viewport_width": "",
                        "google_fonts": "", "device_scale": ""})
    async with httpx.AsyncClient(headers=my_headers) as ses:
            try:
                resp = await ses.post(url, data=data)
                return resp.json()
            except Exception:
                return None


async def html_cssworker(target_html: str):
    url = "https://htmlcsstoimage.com/demo_run"
    my_headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0',
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': 'https://htmlcsstoimage.com/',
        'Content-Type': 'application/json',
        'Origin': 'https://htmlcsstoimage.com',
        'Alt-Used': 'htmlcsstoimage.com',
        'Connection': 'keep-alive',
    }

    data = json.dumps(
        {"html": target_html, "console_mode": "", "url": "", "css": "", "selector": "", "ms_delay": "",
         "render_when_ready": "false", "viewport_height": "", "viewport_width": "",
         "google_fonts": "", "device_scale": ""})

    async with httpx.AsyncClient(headers=my_headers) as ses:
        try:
            resp = await ses.post(url, data=data)
            return resp.json()
        except httpx.NetworkError:
            return None

