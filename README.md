# Iceland Energy Prices for Home Assistant

A Home Assistant integration that monitors electricity prices from all major Icelandic energy providers. Get real-time pricing data from Aurbjörg's comparison service directly in your Home Assistant Energy Dashboard.

## 📊 Features

- **🏷️ Real-time Price Monitoring** - Fetches current electricity prices from Aurbjörg
- **⚡ Energy Dashboard Compatible** - Full integration with Home Assistant's Energy Dashboard
- **🏢 All Major Providers** - Supports all 8 major Icelandic electricity providers
- **📈 Daily Updates** - Automatically updates once per day (configurable)
- **💾 Offline Caching** - Caches last valid data for reliability

## 🇮🇸 Supported Providers

| Provider | General Price | Special Price | Green Energy |
|----------|--------------|---------------|--------------|
| **Orkusalan** | ✅ 12.97 kr/kWh | ✅ 9.92 kr/kWh | ✅ 15.44 kr/kWh |
| **Straumlind** | ✅ 9.92 kr/kWh | ✅ 9.92 kr/kWh | ✅ 10.54 kr/kWh |
| **Orkubú Vestfjarða** | ✅ 9.99 kr/kWh | ✅ 9.99 kr/kWh | ✅ 11.61 kr/kWh |
| **Atlantsorka** | ✅ 9.99 kr/kWh | ✅ 9.99 kr/kWh | ❌ N/A |
| **Orka Heimilanna** | ✅ 9.87 kr/kWh | ✅ 9.87 kr/kWh | ✅ 10.55 kr/kWh |
| **N1 Rafmagn** | ✅ 10.95 kr/kWh | ✅ 10.95 kr/kWh | ✅ 11.57 kr/kWh |
| **Orka náttúrunnar** | ✅ 11.41 kr/kWh | ✅ 11.41 kr/kWh | ✅ 11.91 kr/kWh |
| **HS Orka** | ✅ 12.08 kr/kWh | ✅ 12.08 kr/kWh | ✅ 12.27 kr/kWh |

*Prices shown are examples and will be updated daily from Aurbjörg*

## 📦 Installation

### Direct GitHub Installation (Recommended)

1. **Add Custom Repository:**
   ```
   https://github.com/HermannBjorgvin/Iceland-Energy-Price
   ```
   - Go to **HACS** → **Integrations**
   - Click the three dots menu → **Custom repositories**
   - Add the URL above
   - Category: **Integration**
   - Click **ADD**

2. **Install the Integration:**
   - Search for "Iceland Energy Prices" in HACS
   - Click **DOWNLOAD**
   - Restart Home Assistant
   - Go to **Settings** → **Devices & Services**
   - Click **+ ADD INTEGRATION**
   - Search for "Iceland Energy Prices"
   - Follow the configuration steps

## ⚙️ Configuration

### Initial Setup

1. **Add Integration:**
   - Navigate to **Settings** → **Devices & Services**
   - Click **+ ADD INTEGRATION**
   - Search for "Iceland Energy Prices"
   
2. **Select Your Provider:**
   - Choose your electricity provider from the dropdown
   - Click **Submit**

3. **Configure Options (Optional):**
   - Click **CONFIGURE** on the integration
   - Set update interval (1-168 hours, default: 24)
   - Click **Submit**

### Energy Dashboard Setup

1. **Open Energy Dashboard:**
   - Go to **Settings** → **Dashboards** → **Energy**

2. **Configure Grid Consumption:**
   - Under **Electricity Grid**, click **Add Consumption**
   - Select your energy consumption sensor

3. **Add Energy Costs:**
   - Click **Use an entity with current price**
   - Select one of the price sensors:
     - `sensor.[provider]_general_price` - Standard rate
     - `sensor.[provider]_special_price` - Off-peak rate
     - `sensor.[provider]_origin_guarantee_price` - Green energy rate

4. **Save Configuration:**
   - Click **SAVE**
   - View your energy costs in ISK on the dashboard

## 📊 Sensor Entities

Each configured provider creates 4 sensor entities:

| Entity | Description | Unit | Example |
|--------|-------------|------|---------|
| `sensor.[provider]_general_price` | Standard electricity rate | ISK/kWh | 12.97 |
| `sensor.[provider]_special_price` | Special/off-peak rate | ISK/kWh | 9.92 |
| `sensor.[provider]_origin_guarantee_price` | Renewable energy rate | ISK/kWh | 15.44 |
| `sensor.[provider]_average_cost` | Average annual cost | ISK | 4,133 |

### Entity Attributes

Each sensor includes these attributes:
- `provider`: Name of the electricity provider
- `last_updated`: Timestamp of last successful update
- `currency`: ISK
- `unit`: kr/kWh or ISK

## 🐛 Troubleshooting

### Price Data Not Updating

1. **Check update interval** in integration options
2. **Review logs** for error messages
3. **Manually refresh** via Developer Tools
4. **Verify** Aurbjörg website is accessible

## 🔧 Advanced Configuration

### Multiple Providers

You can add multiple providers for comparison:

1. Add the integration again
2. Select a different provider
3. Both will appear with unique entity IDs

### Custom Update Interval

Via configuration options:
- Minimum: 1 hour
- Maximum: 168 hours (1 week)
- Default: 24 hours
- Recommended: 24 hours (prices update daily)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 🙏 Acknowledgments

- **Aurbjörg** - For providing the price comparison service
