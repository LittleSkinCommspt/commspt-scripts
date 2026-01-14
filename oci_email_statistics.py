from datetime import datetime, timedelta
from oci.loggingsearch import LogSearchClient
from oci.loggingsearch.models import SearchLogsDetails
from oci.util import pytz

from utils.config_manager import config
from utils.send_message import group_message

conf = {
    "region": config.oracle_cloud.region,
    "tenancy": config.oracle_cloud.tenancy,
    "user": config.oracle_cloud.user,
    "fingerprint": config.oracle_cloud.fingerprint,
    "key_file": config.oracle_cloud.key_file,
}

compartment_id = config.oracle_cloud.compartment_id
log_group_id = config.oracle_cloud.log_group_id
log_object_id_accepted = config.oracle_cloud.log_object_id_accepted
log_object_id_relayed = config.oracle_cloud.log_object_id_relayed
log_stream_accepted = f"{compartment_id}/{log_group_id}/{log_object_id_accepted}"
log_stream_relayed = f"{compartment_id}/{log_group_id}/{log_object_id_relayed}"

tz = pytz.timezone("Asia/Shanghai")

datetime_end = datetime.now(tz).replace(hour=5, minute=0, second=0, microsecond=0)  # Today 05:00:00
datetime_start = datetime_end - timedelta(days=1)  # Yesterday 05:00:00

timespan = datetime_end - datetime_start
timespan_str = f"{timespan.days}d" if timespan.days > 0 else f"{timespan.seconds // 3600}h"

details_accepted_total = SearchLogsDetails(
    search_query=f'search "{log_stream_accepted}" | count', time_start=datetime_start, time_end=datetime_end
)
details_accepted_suppressed = SearchLogsDetails(
    search_query=f"search \"{log_stream_accepted}\" | where data.errorType='Recipient suppressed' | count",
    time_start=datetime_start,
    time_end=datetime_end,
)

details_relayed_total = SearchLogsDetails(
    search_query=f'search "{log_stream_relayed}" | count', time_start=datetime_start, time_end=datetime_end
)
details_relayed_bounced = SearchLogsDetails(
    search_query=f"search \"{log_stream_relayed}\" | where data.action='bounce' | count",
    time_start=datetime_start,
    time_end=datetime_end,
)

def get_oci_email_statistics():
    client = LogSearchClient(conf)
        
    resp_accepted_total = client.search_logs(details_accepted_total)
    resp_accepted_suppressed = client.search_logs(details_accepted_suppressed)
    resp_relayed_total = client.search_logs(details_relayed_total)
    resp_relayed_bounced = client.search_logs(details_relayed_bounced)
    
    message = f"""📊 ACS Email 统计 [{timespan_str}]
    Email Accepted Total: {resp_accepted_total.data.results[0].data["count"]}
    Email Accepted Suppressed: {resp_accepted_suppressed.data.results[0].data["count"]}
    Email Relayed Total: {resp_relayed_total.data.results[0].data["count"]}
    Email Relayed Bounced: {resp_relayed_bounced.data.results[0].data["count"]}"""
    
    group_message(config.groups_ids.commspt, message)

if __name__ == "__main__":
    get_oci_email_statistics()