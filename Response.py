
class Response:
    def __init__(self, error_message: str, body: str, xmid: str, machine_name : str, xsable_id: str,subject: str,
                 timestamp: str, sent_to: str, sent_from: str, hrefs: []):
        self.ErrorMessage = error_message
        self.Body = body
        self.XMid = xmid
        self.MachineName = machine_name
        self.XSableId = xsable_id
        self.Subject = subject
        self.TimeStamp = timestamp
        self.SentTo = sent_to
        self.From = sent_from
        self.Hrefs = hrefs


