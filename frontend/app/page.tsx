"use client";

import { useState } from "react";
import { Link } from "@heroui/link";
import { Button } from "@heroui/button";
import { button as buttonStyles } from "@heroui/theme";
import { SearchIcon, GithubIcon } from "@/components/icons";
import { title, subtitle } from "@/components/primitives";

import { Listbox, ListboxSection, ListboxItem } from "@heroui/listbox";
import Search from "@/components/search";

import {
  Modal,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalFooter,
  useDisclosure,
} from "@heroui/modal";

import { Popover, PopoverTrigger, PopoverContent } from "@heroui/popover";

export default function Home() {
  const [isWebsitesModalOpen, setWebsitesModalOpen] = useState(false);
  const [isUpcomingModalOpen, setUpcomingModalOpen] = useState(false);

  const websites = [
    'https://milky-mama.com/pages/customer-reviews',
    'https://row.gymshark.com/products/gymshark-oversized-t-shirt-black-aw21',
    'https://www.allbirds.com/products/mens-tree-dashers-twilight-white-twilight-teal?price-tiers=msrp%2Ctier-1%2Ctier-2',
    'https://2717recovery.com/products/recovery-cream',
    'https://www.shopclues.com/chamria-hing-wati-digestive-mouth-freshner-200-gm-can-pack-of-2-153514795.html',
    'https://beminimalist.co/collections/skin/products/salicylic-lha-2-cleanser'
  ];

  const handleCopy = (url: string) => {
    navigator.clipboard.writeText(url);
  };

  return (
    <section className="flex flex-col items-center justify-center gap-4 py-8 md:py-10">

      <div className="w-full md:w-fit md:max-w-[260px] border-small px-1 py-2 rounded-small border-default-200 dark:border-default-100 md:fixed relative top-[50%] md:left-6 translate-y-[-50%]">
        <Listbox aria-label="Actions">
          <ListboxSection title="Actions">
            <ListboxItem key="k1" onPress={() => setWebsitesModalOpen(true)}>Tested Websites</ListboxItem>
            <ListboxItem key="k2" onPress={() => setUpcomingModalOpen(true)}>Upcoming</ListboxItem>
          </ListboxSection>
        </Listbox>
      </div>

      {/* Hero Section */}
      <div className="inline-block max-w-xl text-center justify-center">
        <span className="text-xs block mb-6 text-gray-600">Powered by AWS, Google AI Studio, Playwright & Next.js</span>
        <span className={title()}>Scrape reviews from&nbsp;</span>
        <span className={title({ color: "violet" })}>product websites</span>
        <br />
        <div className={subtitle({ class: "mt-4" })}>
          Enter the product URL & we will handle the rest 
        </div>
      </div>

      <div className="flex gap-3">
        <Link
          isExternal
          className={buttonStyles({ variant: "bordered", radius: "full" })}
          href="https://github.com/Prashantraj11/Scraper"
        >
          <GithubIcon size={20} />
          GitHub
        </Link>
      </div>

      {/* Input and Button */}
      <Search />

      {/* Tested Websites Modal */}
      <Modal isOpen={isWebsitesModalOpen} size="4xl" onOpenChange={() => setWebsitesModalOpen(false)}>
        <ModalContent>
          {(onClose) => (
            <>
              <ModalHeader className="flex flex-col gap-1">Tested websites</ModalHeader>
              <ModalBody>
                <ul className="flex flex-col gap-2">
                  {websites.map((website) => (
                    <li key={website} className="w-full">
                      <Popover placement="right">
                        <PopoverTrigger>
                          <Button variant="bordered" className="w-full" onPress={() => handleCopy(website)}>
                            {website}
                          </Button>
                        </PopoverTrigger>
                        <PopoverContent>
                          <div className="px-1 py-2">
                            <div className="text-tiny">Copied to clipboard</div>
                          </div>
                        </PopoverContent>
                      </Popover>
                    </li>
                  ))}
                </ul>
              </ModalBody>
              <ModalFooter>
                <Button color="danger" variant="light" onPress={onClose}>
                  Close
                </Button>
              </ModalFooter>
            </>
          )}
        </ModalContent>
      </Modal>

      {/* Upcoming Modal */}
      <Modal isOpen={isUpcomingModalOpen} size="md" onOpenChange={() => setUpcomingModalOpen(false)}>
        <ModalContent>
          {(onClose) => (
            <>
              <ModalHeader className="flex flex-col gap-1">Upcoming</ModalHeader>
              <ModalBody>
                <p>Real-Time Data Streaming</p>
                <p>Enhanced Reliability with an Improved LLM</p>
                <p>Faster Processing with Parallel AWS Task Execution</p>
              </ModalBody>
              <ModalFooter>
                <Button color="danger" variant="light" onPress={onClose}>
                  Close
                </Button>
              </ModalFooter>
            </>
          )}
        </ModalContent>
      </Modal>

    </section>
  );
}
