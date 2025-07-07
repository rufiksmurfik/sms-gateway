package com.smsgateway;

import android.Manifest;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.content.pm.PackageManager;
import android.os.Bundle;
import android.telephony.SmsMessage;
import android.util.Log;
import android.widget.Button;
import android.widget.EditText;
import android.widget.TextView;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;
import androidx.core.app.ActivityCompat;
import androidx.core.content.ContextCompat;

import java.io.IOException;

import okhttp3.Call;
import okhttp3.Callback;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.Response;

public class MainActivity extends AppCompatActivity {
    
    private static final String TAG = "SMSGateway";
    private static final int PERMISSION_REQUEST_CODE = 100;
    
    private TextView statusText;
    private TextView logText;
    private EditText serverUrlEdit;
    private Button saveButton;
    private Button testButton;
    
    private String serverUrl = "http://192.168.1.100:5000"; // Замените на ваш IP
    private OkHttpClient httpClient;
    private SMSReceiver smsReceiver;
    
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        
        initViews();
        initHttpClient();
        requestPermissions();
        setupSMSReceiver();
        
        addLog("Приложение запущено");
        updateStatus("Готов к работе");
    }
    
    private void initViews() {
        statusText = findViewById(R.id.statusText);
        logText = findViewById(R.id.logText);
        serverUrlEdit = findViewById(R.id.serverUrlEdit);
        saveButton = findViewById(R.id.saveButton);
        testButton = findViewById(R.id.testButton);
        
        serverUrlEdit.setText(serverUrl);
        
        saveButton.setOnClickListener(v -> {
            serverUrl = serverUrlEdit.getText().toString().trim();
            if (!serverUrl.startsWith("http")) {
                serverUrl = "http://" + serverUrl;
            }
            Toast.makeText(this, "URL сохранен", Toast.LENGTH_SHORT).show();
            addLog("URL изменен: " + serverUrl);
        });
        
        testButton.setOnClickListener(v -> testConnection());
    }
    
    private void initHttpClient() {
        httpClient = new OkHttpClient();
    }
    
    private void requestPermissions() {
        String[] permissions = {
            Manifest.permission.RECEIVE_SMS,
            Manifest.permission.SEND_SMS,
            Manifest.permission.READ_SMS,
            Manifest.permission.INTERNET
        };
        
        boolean needPermission = false;
        for (String permission : permissions) {
            if (ContextCompat.checkSelfPermission(this, permission) != PackageManager.PERMISSION_GRANTED) {
                needPermission = true;
                break;
            }
        }
        
        if (needPermission) {
            ActivityCompat.requestPermissions(this, permissions, PERMISSION_REQUEST_CODE);
        }
    }
    
    private void setupSMSReceiver() {
        smsReceiver = new SMSReceiver();
        IntentFilter filter = new IntentFilter("android.provider.Telephony.SMS_RECEIVED");
        filter.setPriority(1000);
        registerReceiver(smsReceiver, filter);
        addLog("SMS ресивер активирован");
    }
    
    private void updateStatus(String status) {
        runOnUiThread(() -> statusText.setText("Статус: " + status));
    }
    
    private void addLog(String message) {
        String timestamp = java.text.DateFormat.getTimeInstance().format(new java.util.Date());
        String logEntry = "[" + timestamp + "] " + message;
        
        runOnUiThread(() -> {
            String currentLog = logText.getText().toString();
            String newLog = logEntry + "\\n" + currentLog;
            
            // Ограничиваем лог
            String[] lines = newLog.split("\\n");
            if (lines.length > 20) {
                StringBuilder sb = new StringBuilder();
                for (int i = 0; i < 20; i++) {
                    sb.append(lines[i]).append("\\n");
                }
                newLog = sb.toString();
            }
            
            logText.setText(newLog);
        });
        
        Log.d(TAG, logEntry);
    }
    
    private void testConnection() {
        addLog("Тестируем соединение...");
        updateStatus("Тестирование...");
        
        Request request = new Request.Builder()
                .url(serverUrl + "/status")
                .build();
        
        httpClient.newCall(request).enqueue(new Callback() {
            @Override
            public void onFailure(Call call, IOException e) {
                addLog("❌ Ошибка: " + e.getMessage());
                updateStatus("Ошибка соединения");
            }
            
            @Override
            public void onResponse(Call call, Response response) throws IOException {
                if (response.isSuccessful()) {
                    addLog("✅ Соединение установлено");
                    updateStatus("Подключено к серверу");
                } else {
                    addLog("❌ Ошибка сервера: " + response.code());
                    updateStatus("Ошибка сервера");
                }
                response.close();
            }
        });
    }
    
    private void sendSMSToServer(String phone, String message) {
        addLog("📤 Отправляем SMS на сервер от " + phone);
        
        String url = serverUrl + "/webhook?phone=" + phone + "&mes=" + message + "&id=" + System.currentTimeMillis();
        
        Request request = new Request.Builder()
                .url(url)
                .build();
        
        httpClient.newCall(request).enqueue(new Callback() {
            @Override
            public void onFailure(Call call, IOException e) {
                addLog("❌ Ошибка отправки: " + e.getMessage());
                updateStatus("Ошибка отправки");
            }
            
            @Override
            public void onResponse(Call call, Response response) throws IOException {
                if (response.isSuccessful()) {
                    addLog("✅ SMS отправлено на сервер");
                    updateStatus("SMS обработано");
                } else {
                    addLog("❌ Ошибка сервера: " + response.code());
                    updateStatus("Ошибка сервера");
                }
                response.close();
            }
        });
    }
    
    private class SMSReceiver extends BroadcastReceiver {
        @Override
        public void onReceive(Context context, Intent intent) {
            if ("android.provider.Telephony.SMS_RECEIVED".equals(intent.getAction())) {
                Bundle bundle = intent.getExtras();
                if (bundle != null) {
                    Object[] pdus = (Object[]) bundle.get("pdus");
                    if (pdus != null) {
                        for (Object pdu : pdus) {
                            SmsMessage sms = SmsMessage.createFromPdu((byte[]) pdu);
                            String sender = sms.getDisplayOriginatingAddress();
                            String message = sms.getMessageBody();
                            
                            addLog("📩 SMS от " + sender + ": " + message);
                            updateStatus("Получено SMS от " + sender);
                            
                            sendSMSToServer(sender, message);
                        }
                    }
                }
            }
        }
    }
    
    @Override
    protected void onDestroy() {
        super.onDestroy();
        if (smsReceiver != null) {
            unregisterReceiver(smsReceiver);
        }
    }
    
    @Override
    public void onRequestPermissionsResult(int requestCode, String[] permissions, int[] grantResults) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);
        
        if (requestCode == PERMISSION_REQUEST_CODE) {
            boolean allGranted = true;
            for (int result : grantResults) {
                if (result != PackageManager.PERMISSION_GRANTED) {
                    allGranted = false;
                    break;
                }
            }
            
            if (allGranted) {
                addLog("✅ Все разрешения получены");
                updateStatus("Разрешения получены");
            } else {
                addLog("❌ Нужны разрешения");
                updateStatus("Нужны разрешения");
                Toast.makeText(this, "Дайте все разрешения для работы", Toast.LENGTH_LONG).show();
            }
        }
    }
}
