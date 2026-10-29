// anyIP + Puppeteer: open Chrome through an anyIP proxy
//
// Components: Node.js 18 or newer, plus two packages
//   npm install puppeteer dotenv
// (Puppeteer downloads its own Chrome)
import dotenv from "dotenv";
import puppeteer from "puppeteer";

// 1. The endpoint and your settings
// Copy one line from your anyIP profile (List view) into .env:
//   ANYIP_PROXY=portal.anyip.io:1080:user_XXXX,country_us,...:PASSWORD
// The endpoint is always portal.anyip.io, port 1080.
// Every setting (type, country, city, session) is a flag in the username.
dotenv.config({ path: "../.env", quiet: true });
const [host, port, username, password] =
  process.env.ANYIP_PROXY.split(":");

// 2. Launch Chrome through the proxy
// Chrome only takes the address here and can't log in to SOCKS5: use HTTP.
// The disabled features stop Chrome turning http:// pages into https://.
const browser = await puppeteer.launch({
  headless: false,
  args: [
    `--proxy-server=http://${host}:${port}`,
    "--disable-features=HttpsUpgrades,HttpsFirstBalancedModeAutoEnable",
  ],
});
const page = await browser.newPage();

// 3. Log in to the proxy: the username with its flags, and your password
await page.authenticate({ username, password });

// 4. Check it works: IP-API is the checker anyIP uses for locations
const fields = "country,regionName,city,isp,mobile,proxy";
await page.goto(`http://ip-api.com/json/?fields=${fields}`);
const ip = JSON.parse(await page.$eval("body", (el) => el.innerText));
console.log(`${ip.city}, ${ip.regionName}, ${ip.country} | ${ip.isp}`);
console.log(`mobile: ${ip.mobile} | proxy: ${ip.proxy}`);

await browser.close();
