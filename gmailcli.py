import argparse
import sys
import csv

import os

from gmail import gmail


def parse_args():
	parser = argparse.ArgumentParser(description="gmailcli.py")
	parser.add_argument("-c", "-cred", dest="cred_fn", required=True, help="credential file")
	parser.add_argument("-t", "-tok", dest="tok_fn", required=True, help="token file")
	parser.add_argument("-q", "-query", dest="q", required=True, help="query")
	parser.add_argument("-o", "-outdir", dest="outdir", required=False, default=".", help="output directory")
	parser.add_argument(dest="action", nargs=1, help="action (print_info, save_raw, save_attachments)")
	return parser.parse_args()

ctxt = parse_args()

gm = gmail.Gmail(ctxt.cred_fn, ctxt.tok_fn)
csv_writer = csv.writer(sys.stdout)

if not os.path.exists(ctxt.outdir):
	os.makedirs(ctxt.outdir)

act = {
	"print_info": lambda mid, info: None,
	"save_raw": lambda mid, info: gm.save_message_by_id(mid, filename=os.path.join(ctxt.outdir, mid+".eml")),
	"save_attachments": lambda mid, info: gm.save_attachments_by_id(mid, savedir=os.path.join(ctxt.outdir, mid))
}

message_ids = gm.get_message_ids_by_query(ctxt.q)

for mid in message_ids:
	info = gm.get_info_by_id(mid)

	csv_writer.writerow([info["id"], info["Date"], info["From"], info["To"], info["Subject"]])
	act[ctxt.action[0]](mid, info)
	