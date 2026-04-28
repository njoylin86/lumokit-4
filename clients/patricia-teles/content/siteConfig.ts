import { SiteConfig } from "../generator/types";

export const siteConfig: SiteConfig = {
  siteName: "Patricia Teles",
  location: "Stockholm",
  phone: "079-077 50 65",
  email: "ptelesdoc@gmail.com",
  address: "Jakobsbergsgatan 8, 4tr, 11144 Stockholm",
  pages: [
    { type: "home", title: "Hem" },
    { type: "about", title: "Om oss" },
    { type: "contact", title: "Kontakt" },
    { type: "treatment", title: "Tandimplantat" },
    { type: "treatment", title: "Invisalign" },
    { type: "treatment", title: "Akuttandvård" },
    { type: "treatment", title: "Basundersökning" },
    { type: "treatment", title: "Allmän tandvård" },
    { type: "treatment", title: "Tandvårdsrädsla" }
  ]
};