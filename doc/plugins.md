# Plugins for `xen-bugtool` and overall operation

The capabilities of `xen-bugtool` are extended by a number of plugins.

Plugins are defined using XML files that describe what data to collect
and how to collect it.

This allows for flexible, declarative extension of `xen-bugtool`'s capabilities.

## Top-level Plugin XML Structure

Plugins are loaded by the `load_plugins()` function of `xenserver-status-report`.
It looks in `PLUGIN_DIR` (`/etc/xensource/bugtool`) for XML files.

For example, the `xapi` plugin is defined in `/etc/xensource/bugtool/xapi.xml`.

Each plugin XML file uses a `<capability>` root element with several attributes:

- **`pii`**: If the collected data may contain Personally Identifiable Information.
  - Values: `no`, `yes`, `maybe`, or `if_customized`.
- **`min_size` / `max_size`**:
  - Values: Minimum and maximum expected size (in bytes) of the collected data.
- **`min_time` / `max_time`**:
  - Values: Minimum and maximum expected time (in seconds) to collect the data.
- **`mime`**: The type of data collected.
  - Values: `application/data` or `text/plain` (default).
  - Included in the output of `--capabilities` as the `content-type` attribute
    of the capability. No other use: Not included in the status-report itself.
  - Currently, all currently known plugins use the default of `text/plain`.
- **`checked`**: Whether this plugin is enabled by default.
  - Values: `true` or `false`.
- **`hidden`**: Whether this plugin is hidden from the user interface.
  - Values: `true` or `false`.

### Example `<capability>` Definition

```xml
<capability pii="yes" max_size="16384" max_time="4" checked="true"/>
```

Best practices:

- Set `pii` to indicate if Personally Identifiable Information may be collected.
- Set `max_size` and `max_time` according to the expected maximum size and time

## Defining Data Collection in `/etc/xensource/bugtool/<plugin>/stuff.xml`

The data collection directives are specified in another XML file.

It is found in a subdirectory named after the plugin,
e.g., `/etc/xensource/bugtool/xapi/stuff.xml`.

It contains a single `<collect>` section which defines what data to gather.
The possible subsections of the `<collect>` section are (each of these
may occur multiple times):

- **`<files>`**:
  - Collect a file path, optionally using wildcards. Example:

    ```xml
    <files>/sys/fs/gfs2/*/uuid</files>
    ```

- **`<list recursive="true|false">`**:
  - List the contents of specified directories.
    If `recursive` is `true`, subdirectories are included. Example:

    ```xml
    <list>/var/lib/corosync</list>
    ```

- **`<directory pattern="regex" negate="true|false">basepath</directory>`**:
  - Collect files in `basepath` matching the given `regex` pattern.
    (Or not matching the pattern when `negate="true"`).
    Example:

    ```xml
    <directory pattern=".*xcp-rrdd-plugins\.log.*">/var/log</directory>
    ```

- **`<command label="...">`**: Run the specified command and collect its output.
  - The `label` attribute describes the output. Example:

    ```xml
    <command label="host_data_source_list">/opt/xensource/bin/xe host-data-source-list host=$(/opt/xensource/bin/xe pool-list params=master --minimal)</command>
    ```

### Example `stuff.xml` file from the `xapi` bugtool Plugin

```xml
<collect>
<command label="sr_data_source_list">/opt/xensource/bin/xe sr-list --minimal | tr , '\n' | xargs --verbose -n 1 -I {} /opt/xensource/bin/xe sr-data-source-list uuid={} 2>&amp;1</command>
<files>/etc/stunnel/xapi.conf</files>
<list>/var/lib/corosync</list>
<list recursive="false">/etc/xen/scripts</list>
<directory pattern=".*\.log$" negate="false">/var/log/xen</directory>
</collect>
```

In this example, `2>&amp;1` is the XML-escaped form of the shell redirection `2>&1`,
which redirects `stderr` (file descriptor 2) to `stdout` (file descriptor 1).

### Best Practices for plugin development

- Use `pattern` and `negate` to fine-tune file selection.
- Provide meaningful `label` values for commands.
- Test plugins and ensure they perform within defined time and size limits.
