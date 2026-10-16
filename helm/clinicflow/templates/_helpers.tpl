{{/* Base name for every resource, e.g. "clinicflow" for release "clinicflow". */}}
{{- define "clinicflow.fullname" -}}
{{- if contains .Chart.Name .Release.Name -}}
{{- .Release.Name | trunc 63 | trimSuffix "-" -}}
{{- else -}}
{{- printf "%s-%s" .Release.Name .Chart.Name | trunc 63 | trimSuffix "-" -}}
{{- end -}}
{{- end -}}

{{- define "clinicflow.labels" -}}
helm.sh/chart: {{ .Chart.Name }}-{{ .Chart.Version }}
app.kubernetes.io/name: {{ .Chart.Name }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end -}}

{{/* Selector labels for one component: include "clinicflow.selectorLabels" (dict "ctx" . "component" "backend") */}}
{{- define "clinicflow.selectorLabels" -}}
app.kubernetes.io/name: {{ .ctx.Chart.Name }}
app.kubernetes.io/instance: {{ .ctx.Release.Name }}
app.kubernetes.io/component: {{ .component }}
{{- end -}}

{{- define "clinicflow.image" -}}
{{- $tag := required (printf "%s.image.tag is required (CI sets it to the Git commit SHA)" .component) .image.tag -}}
{{- printf "%s:%s" .image.repository $tag -}}
{{- end -}}
