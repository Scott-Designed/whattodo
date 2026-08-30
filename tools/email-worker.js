// Cloudflare Email Worker — forwards mail sent to notice.place into the inbox.
//
// Cloudflare Email Routing receives the message and hands it to this worker,
// which POSTs it to https://www.notice.place/api/inbox. Nothing here decides
// anything: it reads the message and passes it on. Every judgement about what
// the email means happens in the back of house, where a person is looking.
//
// Two secrets, set with `wrangler secret put` (see CLAUDE.md):
//   INBOX_URL      https://www.notice.place/api/inbox
//   INBOX_SECRET   the same value as INBOX_SECRET in the Vercel project
//
// Cloudflare's free plan allows this. Email Routing itself is free; a worker
// bound to it runs on the free Workers tier.

export default {
  async email(message, env) {
    // 1MB is Cloudflare's own cap on a forwarded message. The endpoint keeps
    // the first 60KB; taking the whole thing here means the truncation
    // decision is made in one place rather than two.
    const raw = await new Response(message.raw).text();

    const body = {
      from:    message.from,
      to:      message.to,
      subject: message.headers.get('subject') || '',
      raw,
    };

    const r = await fetch(env.INBOX_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-inbox-secret': env.INBOX_SECRET,
      },
      body: JSON.stringify(body),
    });

    // Rejecting the message tells the sender it did not arrive, which is true
    // and is better than accepting mail this project then silently drops.
    // Cloudflare retries a thrown error; a reject is final, so only refuse
    // once it is clear the endpoint is answering and simply said no.
    if (!r.ok) {
      const detail = (await r.text()).slice(0, 200);
      if (r.status >= 500) throw new Error(`inbox ${r.status}: ${detail}`);
      message.setReject(`Not accepted (${r.status})`);
    }
  },
};
