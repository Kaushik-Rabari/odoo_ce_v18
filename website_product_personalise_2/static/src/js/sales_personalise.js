/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.WebsiteSale = publicWidget.registry.WebsiteSale.extend({
    storedInputs: {},  // Stores user inputs to retain on variant change

    events: Object.assign({}, publicWidget.registry.WebsiteSale.prototype.events, {
        "input .variant_custom_value": "OnInputCustomValue",
        "change [data-attribute_exclusions]": "_onChangeCombination",
        "change #font_family_selector": "ApplyFontToAllPreviews",
        'click form[action="/shop/cart/update"] .a-submit': '_onClickAddToCart',
        'click .product_detail_img': '_onImageClick',
    }),

    _onImageClick(event) {
        // Select the actual <img> inside the wrapper
        const imageElement = document.querySelector(".product_detail_img img");
    
        if (!imageElement) {
            console.warn("🛑 No image found for click calculation.");
            return;
        }
    
        const rect = imageElement.getBoundingClientRect();
    
        // Get the coordinates relative to the image
        const clickX = event.clientX - rect.left;
        const clickY = event.clientY - rect.top;
    
        // Also calculate as percentage if needed
        const percentX = (clickX / rect.width) * 100;
        const percentY = (clickY / rect.height) * 100;
    
        console.log("📸 Accurate Image Click:", {
            x_px: clickX.toFixed(2),
            y_px: clickY.toFixed(2),
            x_percent: percentX.toFixed(2) + "%",
            y_percent: percentY.toFixed(2) + "%",
        });
    
        alert(`📍 Accurate Click on Image:\nLeft (X): ${clickX.toFixed(2)} px\nTop (Y): ${clickY.toFixed(2)} px`);

        // Optional: dynamically position a marker or text
        const textElement = document.createElement("div");
        textElement.textContent = "📍";
        textElement.style.position = "absolute";
        textElement.style.left = `${clickX}px`;
        textElement.style.top = `${clickY}px`;
        textElement.style.transform = "translate(-50%, -100%)";  // Center the marker a bit above
        textElement.style.pointerEvents = "none";
        textElement.style.fontSize = "18px";
        textElement.style.color = "red";
        textElement.classList.add("click-marker");

        // Clear any existing markers first (optional)
        document.querySelectorAll(".click-marker").forEach(e => e.remove());

        // Append to the container
        imageElement.parentElement.style.position = "relative"; // Ensure relative for correct absolute placement
        imageElement.parentElement.appendChild(textElement);
    },    

    /**
     * Safe override of Add to Cart
     */
    _onClickAddToCart: function (ev) {
        let imageElement = document.querySelector(".product_detail_img img");
        console.log("✅ Found imageElement:", imageElement);

        let textElements = document.querySelectorAll(".custom-preview-text");

        if (!imageElement || textElements.length === 0) {
            alert("Product image or customization text missing!");
            return;
        }
    
        let img = new Image();
        img.crossOrigin = "anonymous";
        // img.src = imageElement.src;
        img.src = imageElement.currentSrc || imageElement.src;    

        img.onload = () => {
            let canvas = document.createElement("canvas");
            let ctx = canvas.getContext("2d");
    
            canvas.width = img.naturalWidth;
            canvas.height = img.naturalHeight;
    
            ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
    
            let imageRect = imageElement.getBoundingClientRect();
            let scaleX = canvas.width / imageRect.width;
            let scaleY = canvas.height / imageRect.height;
    
            textElements.forEach((el) => {
                let text = el.textContent.trim();
                if (!text) return;
    
                let rect = el.getBoundingClientRect();
    
                let x = (rect.left - imageRect.left) * scaleX;
                let y = (rect.top - imageRect.top) * scaleY;
    
                // Extract inline font styles from the DOM (not CSS)
                let computed = window.getComputedStyle(el);
                let fontSizePx = parseFloat(computed.fontSize);
                let fontFamily = computed.fontFamily || 'Arial';
                let fontWeight = computed.fontWeight || 'normal';
                let color = computed.color || '#000000';
    
                let fontSizeCanvas = fontSizePx * scaleY;
    
                // Convert RGB to HEX if needed (canvas prefers HEX for consistency)
                const rgbToHex = (rgb) => {
                    const result = /^rgb\((\d+),\s*(\d+),\s*(\d+)\)$/.exec(rgb);
                    return result
                        ? "#" + result.slice(1).map(x => ('0' + parseInt(x).toString(16)).slice(-2)).join('')
                        : rgb;
                };
    
                ctx.font = `${fontWeight} ${fontSizeCanvas}px ${fontFamily}`;
                ctx.fillStyle = rgbToHex(color);
                ctx.textBaseline = 'top';
                ctx.fillText(text, x, y);
            });
    
            let imageData = canvas.toDataURL("image/png");
            console.log("imgData---------", imageData)
            sessionStorage.setItem("customized_image_preview", imageData);
    
            // Post image to backend
            setTimeout(() => {
                let form = document.createElement("form");
                form.action = "/custom_image_save";
                form.method = "POST";
        
                let inputImage = document.createElement("input");
                inputImage.type = "hidden";
                inputImage.name = "image_data";
                inputImage.value = imageData;
                form.appendChild(inputImage);
        
                let productId = document.querySelector('input[name="product_id"]')?.value || '';
                let inputProduct = document.createElement("input");
                inputProduct.type = "hidden";
                inputProduct.name = "product_id";
                inputProduct.value = productId;
                form.appendChild(inputProduct);
        
                let inputUrl = document.createElement("input");
                inputUrl.type = "hidden";
                inputUrl.name = "redirect_url";
                inputUrl.value = window.location.href;
                form.appendChild(inputUrl);
        
                document.body.appendChild(form);
                form.submit();
            }, 1000);
        }
        console.log("img---------", img)
        img.onerror = () => {
            alert("Could not load base image.");
        };
    },

    /**
     * Stores user inputs before changing variants.
     */
    _storeLiveInputs: function () {
        this.storedInputs = {}; // Reset stored inputs
        document.querySelectorAll(".variant_custom_value").forEach((input) => {
            let inputName = input.getAttribute("data-attribute_value_name");
            if (inputName) {
                this.storedInputs[inputName] = input.value;
            }
        });
    },

    /**
     * Restores stored user inputs after variant change.
     */
    _restoreLiveInputs: function () {
        document.querySelectorAll(".variant_custom_value").forEach((input) => {
            let inputName = input.getAttribute("data-attribute_value_name");
            if (inputName && this.storedInputs.hasOwnProperty(inputName)) {
                input.value = this.storedInputs[inputName];

                // Simulate user input to update live preview
                this.OnInputCustomValue({ target: input });
            } else {
            }
        });
    },

    /**
     * Updates live preview text dynamically as user types.
     */
    OnInputCustomValue: function (ev) {
        let inputField = ev.target;
        let inputValue = inputField.value;
        let attributeName = inputField.dataset.attribute_value_name;
    
        if (!attributeName) return;
    
        let liveTextElement = document.querySelector(`#customText_${attributeName}`);
        if (liveTextElement) {
            liveTextElement.textContent = inputValue;
    
            let fontSelector = document.getElementById("font_family_selector");
            if (fontSelector) {
                liveTextElement.style.fontFamily = fontSelector.value;
            }
        } else {
            // console.warn(`Non Matching Element found for: customText_${attributeName}`);
        }
    },

    /**
     * Applies the selected font to all preview elements, even if they already contain text.
     */
    ApplyFontToAllPreviews: function () {
        const fontSelector = document.getElementById("font_family_selector");
        if (!fontSelector) return;

        const selectedFont = fontSelector.value;

        document.querySelectorAll("div[id^='customText_']").forEach((div) => {
            div.style.fontFamily = selectedFont;
        });
    },

    /**
     * Handles variant selection, applies styling, and restores previous inputs.
     */
    _onChangeCombination: function (ev, $parent, combination) {
        this._storeLiveInputs();  // Store inputs before changing variant

        const res = this._super.apply(this, arguments); // Call Odoo base logic
        let attributes = combination.custom_input_style || {};

        // Show/hide relevant attribute rows
        let rows = document.querySelectorAll("#product_attributes_simple tr");
        rows.forEach(row => {
            let attrName = row.querySelector("td span:first-child")?.innerText.trim();
            if (attrName) {
                if (Object.values(attributes).some(attr => attr.name === attrName)) {
                    row.classList.remove("d-none");
                } else {
                    row.classList.add("d-none");
                }
            }
        });

        // Apply styles to live preview text
        Object.keys(attributes).forEach((attrName) => {
            this.applyStyles(`customText_${attrName}`, attributes[attrName]);
        });

        this.toggleAttributeVisibility(combination);
        this._restoreLiveInputs();  // Restore stored inputs after variant change

        return res;
    },

    /**
     * Applies styles dynamically to the live preview.
     */
    applyStyles: function (elementId, attrData) {
        let element = document.getElementById(elementId);
        if (!element || !attrData) return;

        Object.assign(element.style, {
            top: attrData.top ? `${attrData.top}px` : "",
            left: attrData.left ? `${attrData.left}px` : "",
            color: attrData.font_color || "",
            fontSize: attrData.font_size || "",
            // fontFamily: attrData.font_family || "",
        });
    },

    /**
     * Toggles the visibility of elements based on attributes.
     */
    toggleAttributeVisibility: function (combination) {
        let hasVisibleFreeText = false;

        document.querySelectorAll('.variant_attribute').forEach(function (attributeElement) {
            let attributeName = attributeElement.getAttribute('data-attribute_name');
            let isFreeText = !!attributeElement.querySelector('.variant_custom_value'); // Check if it's a Free Text field
            let customAttr = combination.custom_input_style ? combination.custom_input_style[attributeName] : null;

            if (!isFreeText) {
                return; // Skip non-Free Text fields
            }
            if (!customAttr) {
                attributeElement.classList.add('d-none'); // Hide only if the Free Text field is not available
            } else {
                attributeElement.classList.remove('d-none'); // Show if the attribute is present in the variant
                hasVisibleFreeText = true;
            }
        });
        // Now toggle the font selector based on any visible Free Text field
        const fontSelector = document.querySelector("#font_family_dropdown");
        if (fontSelector) {
            fontSelector.style.display = hasVisibleFreeText ? 'block' : 'none';
        }
    },
});



// import publicWidget from "@web/legacy/js/public/public_widget";

// publicWidget.registry.WebsiteSale = publicWidget.registry.WebsiteSale.extend({
//     storedInputs: {},  // Stores user inputs to retain on variant change

//     events: Object.assign({}, publicWidget.registry.WebsiteSale.prototype.events, {
//         "input .variant_custom_value": "OnInputCustomValue",
//         "change [data-attribute_exclusions]": "_onChangeCombination",
//     }),

//     /**
//      * Stores user inputs before changing variants.
//      */
//     _storeLiveInputs: function () {
//         this.storedInputs = {}; // Reset stored inputs
//         document.querySelectorAll(".variant_custom_value").forEach((input) => {
//             let inputName = input.getAttribute("data-attribute_value_name");
//             if (inputName) {
//                 this.storedInputs[inputName] = input.value;
//             }
//         });
//     },

//     /**
//      * Restores stored user inputs after variant change.
//      */
//     _restoreLiveInputs: function () {
//         document.querySelectorAll(".variant_custom_value").forEach((input) => {
//             let inputName = input.getAttribute("data-attribute_value_name");
//             if (inputName && this.storedInputs.hasOwnProperty(inputName)) {
//                 input.value = this.storedInputs[inputName];

//                 // Simulate user input to update live preview
//                 this.OnInputCustomValue({ target: input });
//             } else {
//             }
//         });
//     },

//     /**
//      * Updates live preview text dynamically as user types.
//      */
//     OnInputCustomValue: function (ev) {
//         let inputField = ev.target;
//         let inputValue = inputField.value;
//         let attributeName = inputField.dataset.attribute_value_name;

//         if (!attributeName) return;

//         let liveTextElement = document.querySelector(`#customText_${attributeName}`);
//         if (liveTextElement) {
//             liveTextElement.textContent = inputValue;
//         } else {
//         }
//     },

//     /**
//      * Handles variant selection, applies styling, and restores previous inputs.
//      */
//     _onChangeCombination: function (ev, $parent, combination) {
//         this._storeLiveInputs();  // Store inputs before changing variant

//         const res = this._super.apply(this, arguments); // Call Odoo base logic
//         let attributes = combination.custom_input_style || {};

//         // Show/hide relevant attribute rows
//         let rows = document.querySelectorAll("#product_attributes_simple tr");
//         rows.forEach(row => {
//             let attrName = row.querySelector("td span:first-child")?.innerText.trim();
//             if (attrName) {
//                 if (Object.values(attributes).some(attr => attr.name === attrName)) {
//                     row.classList.remove("d-none");
//                 } else {
//                     row.classList.add("d-none");
//                 }
//             }
//         });

//         // Apply styles to live preview text
//         Object.keys(attributes).forEach((attrName) => {
//             this.applyStyles(`customText_${attrName}`, attributes[attrName]);
//         });

//         this.toggleAttributeVisibility(combination);
//         this._restoreLiveInputs();  // Restore stored inputs after variant change

//         return res;
//     },

//     /**
//      * Applies styles dynamically to the live preview.
//      */
//     applyStyles: function (elementId, attrData) {
//         let element = document.getElementById(elementId);
//         if (!element || !attrData) return;

//         Object.assign(element.style, {
//             top: attrData.top ? `${attrData.top}px` : "",
//             left: attrData.left ? `${attrData.left}px` : "",
//             color: attrData.font_color || "",
//             fontSize: attrData.font_size || "",
//             fontFamily: attrData.font_family || "",
//         });
//     },

//     /**
//      * Toggles the visibility of elements based on attributes.
//      */
//     toggleAttributeVisibility: function (combination) {
//         document.querySelectorAll('.variant_attribute').forEach(function (attributeElement) {
//             let attributeName = attributeElement.getAttribute('data-attribute_name');
//             let isFreeText = !!attributeElement.querySelector('.variant_custom_value'); // Check if it's a Free Text field
//             let customAttr = combination.custom_input_style ? combination.custom_input_style[attributeName] : null;

//             if (!isFreeText) {
//                 return; // Skip non-Free Text fields
//             }
//             if (!customAttr) {
//                 attributeElement.classList.add('d-none'); // Hide only if the Free Text field is not available
//             } else {
//                 attributeElement.classList.remove('d-none'); // Show if the attribute is present in the variant
//             }
//         })
//     }
// });
