import { SiteConfig } from "../generator/types";

export const siteConfig: SiteConfig = {
  siteName: "Älvsjö Tandvård",
  location: "Älvsjö, Stockholm",
  phone: "08-12 85 45 55",
  email: "boka@alvsjotandvard.se",
  address: "Prästgårdsgränd 4, 125 44 Älvsjö",
  useScrapedContent: true,
  pages: [
    { type: "home", title: "Hem" },
    { type: "about", title: "Om oss" },
    { type: "treatment", title: "Akuttandvård" },
    { type: "treatment", title: "Implantat" },
    { type: "treatment", title: "Karies/Hål i tanden" },
    { type: "treatment", title: "Tandblekning" },
    { type: "treatment", title: "Tandfasader veneers" },
    { type: "treatment", title: "Tandreglering" },
    { type: "treatment", title: "Tandsten/Tandhygienist" },
    { type: "treatment", title: "Tandvårdsrädsla/Tandläkarskräck" },
    { type: "treatment", title: "Tillhör du riskgrupp?" },
    { type: "info", title: "Räntefritt" },
    { type: "info", title: "Barnspecialist" },
    { type: "info", title: "Lista dig" },
    { type: "info", title: "Remiss" },
    { type: "info", title: "Kampanjer" },
    { type: "info", title: "Mina tider" },    
    { type: "contact", title: "Kontakt" }
  ]
};
