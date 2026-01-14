from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import oci
from oci.loggingsearch import LogSearchClient
from oci.loggingsearch.models import SearchLogsDetails

from utils.config_manager import config as CONFIG
from utils.send_message import group_message

config = oci.config.from_file("./.oci/config")

client = LogSearchClient(config)

compartment_id = config["tenancy"]

# time range
timezone = ZoneInfo("Asia/Shanghai")
datetime_end = datetime.now(timezone).replace(hour=5, minute=0, second=0, microsecond=0)  # Today 05:00:00
datetime_start = datetime_end - timedelta(days=1)  # Yesterday 05:00:00

log_stream_accepted = f"{compartment_id}/{CONFIG.oci.log_group_id}/{CONFIG.oci.log_object_id_accepted}"
log_stream_relayed = f"{compartment_id}/{CONFIG.oci.log_group_id}/{CONFIG.oci.log_object_id_relayed}"

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

resp_accepted_total = client.search_logs(details_accepted_total)
resp_accepted_suppressed = client.search_logs(details_accepted_suppressed)
resp_relayed_total = client.search_logs(details_relayed_total)
resp_relayed_bounced = client.search_logs(details_relayed_bounced)

# assert
assert resp_accepted_total, "Failed to get accepted total"
assert resp_accepted_suppressed, "Failed to get accepted suppressed"
assert resp_relayed_total, "Failed to get relayed total"
assert resp_relayed_bounced, "Failed to get relayed bounced"

accepted_total = resp_accepted_total.data.results[0].data["count"]
accepted_suppressed = resp_accepted_suppressed.data.results[0].data["count"]
relayed_total = resp_relayed_total.data.results[0].data["count"]
relayed_bounced = resp_relayed_bounced.data.results[0].data["count"]

# send message
message = f"""📊 OCI Email 统计 
--- {datetime_start.strftime("%m-%d %H:%M")} ~ {datetime_end.strftime("%m-%d %H:%M")} ---

Accepted Total: {accepted_total}
Accepted Suppressed: {accepted_suppressed}
Relayed Total: {relayed_total}
Relayed Bounced: {relayed_bounced}
"""

print(message)

group_message(CONFIG.groups_ids.commspt, message)
