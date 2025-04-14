import re
import json
import logging
from urllib.parse import unquote

from Request import Payload
from utm import Utm
import requests

from azure.identity import ClientSecretCredential
from msgraph.core import GraphClient

from bs4 import BeautifulSoup, SoupStrainer


def main() -> None:
    UTM_GROUP_REGEX = r"(?!&)utm_[^=]*=[^&]*"
    logger = logging.getLogger(__name__)

    # Using Microsoft Graph API to authenticate into rp@godaddy.com inbox
    credential = ClientSecretCredential(
        tenant_id='d5f1622b-14a3-45a6-b069-003f8dc4851f',
        client_secret='FBO8Q~pu1Sn_r9k3aUyD6Fbqemg5BczC2EsQXbKL',
        client_id='dace6567-8b32-4fb3-b253-042c0521e258'
    )
    client = GraphClient(credential=credential)
    select = 'from,subject,body,receivedDateTime'
    number_of_emails_to_retrieve = 2

    response = client.get(
        f'https://graph.microsoft.com/v1.0/users/rp@godaddy.com/mailFolders/inbox/messages?$select={select}'
        f'&$top={number_of_emails_to_retrieve}',
        scopes=['https://graph.microsoft.com/.default']
    )

    top_retrieved_emails = response.json()['value']
    only_godaddy_emails = [
        email for email in top_retrieved_emails
        if 'godaddy.com' in email['from']['emailAddress']['address']
    ]

    if len(only_godaddy_emails) == 0:
        print("-----There are no emails from @godaddy.com!!!-----")

    urls = []
    for message in only_godaddy_emails:
        for link in BeautifulSoup(message['body']['content'], features='html.parser', parse_only=SoupStrainer('a')):
            if link.has_attr('href') and 'tel' not in link['href']:
                urls.append(link['href'])

    if len(only_godaddy_emails) != 0 and len(urls) == 0:
        print(f"-----There are {len(only_godaddy_emails)} emails from @godaddy.com, but 0 URLs!!!-----")

    # ALso add URL are valid, 200 Response Check.
    for url in urls:
        try:
            if url.split(':')[0] == 'tel':
                logger.info("*" * 80)
                logger.warning(f"the embedded link is a telephone number {url}, bypassing for now")
                logger.info("*" * 80)
                # elif url.split(':')[0]=='mailto':
                #     logger.info("*" * 80)
                #     logger.warning(f"the embedded link is an email address {url}, bypassing for now")
                #     logger.info("*" * 80)
                continue
            response = requests.request("GET", url)
            print("original", url)
            converted_url = response.url

            # Adding headers with User-Agent similar to how a normal browser accesses webpages, helps us avoid 403s
            # Certain pages reject GET requests that do not identify a User-Agent
            # https://stackoverflow.com/questions/38489386/python-requests-403-forbidden
            headers = {
                'User-Agent':
                    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                    'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36'
            }

            response_c_url = requests.request("GET", converted_url, headers=headers)
            # TODO check for Response code here.
            if response_c_url.status_code != 200:
                logger.warning(f"The redirected url doesnt lead to a valid page/  doesn't return a valid 200 response, "
                               f"but {response.status_code}  code instead")

            # Transforming the UTF-8 encoded bytes for & and =,
            # so as to make sure the url are parsed correctly
            converted_url = unquote(converted_url)
            print("converted url", converted_url)
            matches = re.findall(UTM_GROUP_REGEX, converted_url)

            # reset the utm_object
            utm_object = Utm()

            for match in matches:
                if "utm_source" in match:
                    utm_object.utm_source = match.split('=')[1]
                if "utm_medium" in match:
                    utm_object.utm_medium = match.split('=')[1]
                if "utm_campaign" in match:
                    temp = match.split('=')[1]
                    res = temp.split('_')
                    if len(res) != 5:
                        logger.info("*" * 80)
                        logger.warning(
                            f"The utm_campaign for the url has {len(res)} elements when the expected is 5 elements")
                        logger.warning(f"The utm_campaign element is {temp}")
                        logger.info("*" * 80)
                    else:
                        utm_object.utm_campaign["marketid"] = res[0]
                        utm_object.utm_campaign["product"] = res[1]
                        utm_object.utm_campaign["channel"] = res[2].split('-')[0]
                        utm_object.utm_campaign["budgettype"] = res[2].split('-')[1]
                        utm_object.utm_campaign["funnel"] = res[3]
                        utm_object.utm_campaign["emailsource"] = res[4]
                if "utm_content" in match:
                    temp = match.split('=')[1]
                    res_content = temp.split('_')
                    if len(res_content) != 8:
                        logger.info("*" * 80)
                        logger.warning(
                            f"The utm_content for the url has {len(res_content)} elements when the expected is 8 elements",
                            len(res_content))
                        logger.warning(f"The utm_campaign element is {temp}")
                        logger.info("*" * 80)
                        # utm_object.utm_content["date"] = res_content[0]
                        # utm_object.utm_content["templateid"] = res_content[1]
                        # utm_object.utm_content["pod"] = res_content[2]
                        # utm_object.utm_content["emailproduct"] = res_content[3]
                        # utm_object.utm_content["cat"] = res_content[4]
                        # utm_object.utm_content["subcat"] = res_content[5]
                        # utm_object.utm_content["ISC"] = res_content[6]
                        # utm_object.utm_content["contentblockname"] = res_content[7]
                    else:
                        utm_object.utm_content["date"] = res_content[0]
                        utm_object.utm_content["templateid"] = res_content[1]
                        utm_object.utm_content["pod"] = res_content[2]
                        utm_object.utm_content["emailproduct"] = res_content[3]
                        utm_object.utm_content["cat"] = res_content[4]
                        utm_object.utm_content["subcat"] = res_content[5]
                        utm_object.utm_content["ISC"] = res_content[6]
                        utm_object.utm_content["contentblockname"] = res_content[7]
            print("UTM PARAMS")
            print("-" * 45)
            print(json.dumps(utm_object.__dict__, indent=4))
            print("*" * 180)
        except Exception as e:
            print("-----Error validating URL!-----")
            print(e)


if __name__ == "__main__":
    main()