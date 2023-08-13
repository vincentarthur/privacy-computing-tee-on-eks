import React from 'react';
import SideNavigation from '@cloudscape-design/components/side-navigation';

const navItems = [
    {
        type: "section",
        text: "HCLS Use Case",
        items: [
            {
                type: "link",
                text: "Breast Cancer Classification",
                href: "/breast_cancer_classification"
            },
            // {
            //     type: "link",
            //     text: "Protein Analysis",
            //     href: "#"
            // }

        ]
    }
];

export function CustomNavi() {
    const [activeHref, setActiveHref] = React.useState(
        "#/Search"
    );
    return (
        <SideNavigation
            activeHref={activeHref}
            header={{text: "Privacy Preserving Computing - TEE"}}
            items={navItems}
            onFollow={event => {
                if (!event.detail.external) {
                    setActiveHref(event.detail.href);
                }
            }}
        />
    );
}