import json
import smtplib
import requests
import warnings
import configparser
from bs4 import BeautifulSoup
warnings.filterwarnings("ignore")
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def html_to_json(content, indent=None):
    soup = BeautifulSoup(content, "html.parser")
    rows = soup.find_all("tr")
    headers = {}
    thead = soup.find("thead")
    if thead:
        thead = thead.find_all("th")
        for i in range(len(thead) - 1):
            headers[i] = thead[i + 1].text.strip().lower()
    data = []
    for row in rows:
        cells = row.find_all("td")
        if thead:
            items = {}
            if len(cells) > 0:
                for index in headers:
                    if index < 6:
                        items[headers[index]] = cells[index].text
        else:
            items = []
            for index in cells:
                items.append(index.text.strip())
        if items:
            data.append(items)
    return json.dumps(data, indent=indent)


if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.read('config.ini')
    config = config['credentials']
    url = "https://dirstudio.laziodisco.it/"
    url_1 = "https://dirstudio.laziodisco.it/Home/StoricoEsitiPagamenti"

    # Get credentials
    credentials = {"username": "{}".format(config['username']), "password": "{}".format(config['password'])}
    sender_email = config['sender_email']
    receiver_email = config['receiver_email']
    app_password = config['app_password']

    # Create a session to store your cookies
    session = requests.Session()
    response = session.post(url, data=credentials, verify=False)
    res = session.get(url_1)
    output = html_to_json(res.text)
    json_object = json.loads(output)

    # create message object instance
    msg = MIMEMultipart()
    password = config['app_password']
    msg['From'] = config['sender_email']
    msg['To'] = config['receiver_email']
    msg['Subject'] = "LAZIODISCO"

    table_data = []
    for item in range(len(json_object)):
        table_data.append(json_object[item])

    html = """\
    <html>
      <head></head>
      <body>
        <table>
          <thead>
            <tr>
              <th>{Storico delle domande di partecipazione ai concorsi banditi da DiSCo}</th>
            </tr>
          </thead>
          <tbody>
    """

    for row in table_data[:]:
        html += f"<tr><td>{row}</td></tr>"

    html += """
          </tbody>
        </table>
      </body>
    </html>
    """

    # attach the body to the message
    body = MIMEText(html, 'html')
    msg.attach(body)
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(msg['From'], password)
    server.sendmail(msg['From'], msg['To'], msg.as_string())
    server.quit()
